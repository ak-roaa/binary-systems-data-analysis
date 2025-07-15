import numpy as np
import pandas as pd
import sys
import os
from numba import njit, prange
from scipy.spatial import cKDTree
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path to allow relative imports
sys.path.insert(0, os.path.abspath('..'))
from . import demarcators


@njit(parallel=True)
def _numba_mask(arrays, centers, margins):
    """
    Compute a boolean mask for columns (rows in original DataFrame) 
    where all values fall within [center - margin, center + margin].

    This function is JIT-compiled with Numba for parallel execution.

    Parameters
    ----------
    arrays : np.ndarray, shape (n_cols, n_rows)
        2D array where each row corresponds to a feature and each column is a sample.
    centers : np.ndarray, shape (n_cols,)
        Center values for each feature.
    margins : np.ndarray, shape (n_cols,)
        Allowed error margins for each feature.

    Returns
    -------
    mask : np.ndarray of bool, shape (n_rows,)
        Boolean mask where True means the column satisfies all feature bounds.
    """
    n_cols, n_rows = arrays.shape
    mask = np.ones(n_rows, dtype=np.bool_)
    for j in prange(n_rows):
        for i in range(n_cols):
            v = arrays[i, j]
            c = centers[i]
            e = margins[i]
            if v < c - e or v > c + e:
                mask[j] = False
                break
    return mask


def filter_df(df, margins):
    """
    Filter DataFrame rows using column-wise margins.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with numeric columns.
    margins : dict[str, list[float, float]]
        Dictionary mapping column names to [center, margin] pairs.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame containing only rows that fall within the specified bounds.

    Raises
    ------
    KeyError
        If any key in `margins` is missing from `df`.
    """
    cols = list(margins)
    for col in cols:
        if col not in df.columns:
            raise KeyError(f"Column {col!r} not found in DataFrame.")

    centers = np.array([margins[col][0] for col in cols], dtype=float)
    errs = np.array([margins[col][1] for col in cols], dtype=float)
    arr = np.vstack([df[col].to_numpy() for col in cols])
    mask = _numba_mask(arr, centers, errs)
    return df.loc[mask].copy()


def process_df(df, margins, center_vec, features):
    """
    Process a single DataFrame to find the closest matching row to the center vector.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame to process.
    margins : dict[str, list[float, float]]
        Mapping of features to [center, margin] values.
    center_vec : np.ndarray
        Vector of target feature values.
    features : list[str]
        List of feature column names to consider.

    Returns
    -------
    dict or None
        Dictionary with keys: 'df', 'filtered', 'row', 'dist', 'orig_idx', 
        or None if no valid row was found.
    """
    filtered = filter_df(df, margins)
    if filtered.empty:
        return None

    pts = filtered[features].to_numpy()
    mask = np.isfinite(pts).all(axis=1)
    if not mask.all():
        filtered = filtered.iloc[mask]
        pts = pts[mask]
    if pts.size == 0:
        return None

    if len(pts) == 1:
        dist = np.linalg.norm(center_vec - pts[0])
        idx = 0
    else:
        tree = cKDTree(pts)
        dist, idx = tree.query(center_vec, k=1)

    orig_idx = filtered.index[idx]
    return {
        'df': df,
        'filtered': filtered,
        'row': df.loc[orig_idx],
        'dist': dist,
        'orig_idx': orig_idx
    }


def find_closest_system_parallel(dfs, margins, max_workers=4):
    """
    Find the closest matching system across multiple DataFrames in parallel.

    Parameters
    ----------
    dfs : list of pd.DataFrame
        List of candidate DataFrames.
    margins : dict[str, list[float, float]]
        Feature-specific center and margin bounds.
    max_workers : int, optional
        Number of threads to use in the thread pool (default is 4).

    Returns
    -------
    tuple
        (original DataFrame, filtered DataFrame, best matching row as pd.Series)

    Raises
    ------
    ValueError
        If no matching system was found.
    """
    features = list(margins.keys())
    center_vec = np.array([margins[c][0] for c in features], dtype=float)

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_df, df, margins, center_vec, features) for df in dfs]
        for future in futures:
            res = future.result()
            if res is not None:
                results.append(res)

    if not results:
        raise ValueError("No match found with any system in the database for the given values.")

    best = min(results, key=lambda r: r['dist'])
    return best['df'], best['filtered'], best['row']


def estimate_nova(dfs, margins, max_workers=4):
    """
    Estimate how far into a nova eruption cycle the matched event occurred.

    Parameters
    ----------
    dfs : list of pd.DataFrame
        List of candidate system DataFrames.
    margins : dict[str, list[float, float]]
        Column-wise center and error margins.
    max_workers : int, optional
        Number of threads to use for parallel search (default is 4).

    Returns
    -------
    float
        Time elapsed since the start of the nova eruption cycle for the matched row.
        Returns -1 if no match was found.

    Raises
    ------
    ValueError
        If no valid row is found across all systems.
    """
    df, filtered_df, closest_row = find_closest_system_parallel(dfs, margins, max_workers)
    if not closest_row.empty:
        cycle = closest_row["cycle"]
        time = closest_row["time"]

        mask_ej = df["accumulated mass"] < 0
        eruption_outset_row_idx = df.loc[mask_ej].index[0] if mask_ej.any() else None
        return time - df.loc[eruption_outset_row_idx, "time"]

        # cycle_delimiters = demarcators.demarcate_nova_eruptions(df)
        #return time - cycle_delimiters[cycle][0]
    else:
        return -1
