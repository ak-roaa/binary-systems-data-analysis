import numpy as np
import pandas as pd
from numba import njit, prange
from scipy.spatial import cKDTree
from concurrent.futures import ProcessPoolExecutor


# ---------- NUMBA FILTERING ----------

@njit(parallel=True)
def _numba_mask_optimized(arrays, lower_bounds, upper_bounds):
    """
    Fast boolean mask computation using precomputed bounds.

    Parameters
    ----------
    arrays : np.ndarray, shape (n_features, n_samples)
        Feature matrix.
    lower_bounds : np.ndarray
        Lower bounds for each feature.
    upper_bounds : np.ndarray
        Upper bounds for each feature.

    Returns
    -------
    np.ndarray
        Boolean mask for columns that fall within the bounds.
    """
    n_features, n_samples = arrays.shape
    mask = np.ones(n_samples, dtype=np.bool_)

    for j in prange(n_samples):
        for i in range(n_features):
            val = arrays[i, j]
            if val < lower_bounds[i] or val > upper_bounds[i]:
                mask[j] = False
                break
    return mask


# ---------- DATA FILTERING ----------

def filter_dataframe(df, margins):
    """
    Filters DataFrame rows using per-feature center ± margin bounds.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    margins : dict[str, tuple[float, float]]
        Dictionary mapping column name to (center, margin).

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame.
    """
    features = list(margins.keys())
    centers = np.array([margins[col][0] for col in features], dtype=float)
    errors = np.array([margins[col][1] for col in features], dtype=float)
    lowers = centers - errors
    uppers = centers + errors

    # Shape: (n_features, n_samples)
    arr = np.asfortranarray([df[col].to_numpy() for col in features])
    mask = _numba_mask_optimized(arr, lowers, uppers)
    return df.loc[mask].copy()


# ---------- SINGLE-DATAFRAME SEARCH ----------

def search_dataframe(df, margins, center_vec, features):
    """
    Search for closest matching row in a single DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
    margins : dict[str, tuple[float, float]]
    center_vec : np.ndarray
    features : list[str]

    Returns
    -------
    dict or None
    """
    filtered = filter_dataframe(df, margins)
    if filtered.empty:
        return None

    points = filtered[features].to_numpy()
    mask = np.isfinite(points).all(axis=1)

    if not mask.any():
        return None

    points = points[mask]
    filtered = filtered.iloc[mask]

    if len(points) == 1:
        dist = np.linalg.norm(center_vec - points[0])
        idx = 0
    else:
        tree = cKDTree(points)
        dist, idx = tree.query(center_vec)

    orig_idx = filtered.index[idx]
    return {
        'df': df,
        'filtered': filtered,
        'row': df.loc[orig_idx],
        'dist': dist,
        'orig_idx': orig_idx
    }


# ---------- PARALLEL SEARCH ----------

def find_closest_match(dfs, margins, max_workers=4):
    """
    Search all systems in parallel for the best match.

    Parameters
    ----------
    dfs : list[pd.DataFrame]
    margins : dict[str, tuple[float, float]]
    max_workers : int

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame, pd.Series]

    Raises
    ------
    ValueError
        If no match is found.
    """
    features = list(margins.keys())
    center_vec = np.array([margins[feat][0] for feat in features], dtype=float)

    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(search_dataframe, df, margins, center_vec, features)
            for df in dfs
        ]
        for future in futures:
            res = future.result()
            if res is not None:
                results.append(res)

    if not results:
        raise ValueError("No match found across any system.")

    best = min(results, key=lambda r: r['dist'])
    return best['df'], best['filtered'], best['row']


# ---------- NOVA ESTIMATION ----------

def estimate_nova_time(dfs, margins, max_workers=4):
    """
    Estimate time since start of nova eruption cycle.

    Parameters
    ----------
    dfs : list[pd.DataFrame]
    margins : dict[str, tuple[float, float]]
    max_workers : int

    Returns
    -------
    float
        Time since eruption start. Returns -1 if no match is found.
    """
    try:
        df, _, row = find_closest_match(dfs, margins, max_workers)
    except ValueError:
        return -1

    time = row["time"]

    mask_ejection = df["accumulated mass"] < 0
    if not mask_ejection.any():
        return -1

    eruption_idx = df.loc[mask_ejection].index[0]
    eruption_time = df.loc[eruption_idx, "time"]

    return time - eruption_time
