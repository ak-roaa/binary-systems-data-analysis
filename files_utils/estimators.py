import numpy as np
import pandas as pd
import sys
import os
from numba import njit, prange
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.abspath('..'))
from . import demarcators


def add_column_to_df(df, source_file, key_column, new_column_name, sheet_name):
    """
    Merges a specific column from a CSV or Excel file into an existing DataFrame based on a common key column
    (usually cycle number).

    Parameters:
    - df (pd.DataFrame): The existing DataFrame.
    - source_file (str): Path to the source file (CSV or Excel).
    - key_column (str): The column name to merge on.
    - new_column_name (str): The name of the new column to add.
    - sheet_name (str, optional): The sheet name in the source Excel file. Default is None.

    Returns:
    - pd.DataFrame: The updated DataFrame with the new column added.
    """
    # Check the file extension to determine the reading method
    if source_file.endswith('.csv'):
        source_df = pd.read_csv(source_file)
    elif source_file.endswith('.xlsx'):
        source_df = pd.read_excel(source_file, sheet_name=sheet_name,  engine="openpyxl")
    else:
        raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")

    # Ensure the key column exists in both DataFrames
    if key_column not in df.columns or key_column not in source_df.columns:
        raise ValueError(f"Key column '{key_column}' must exist in both DataFrames.")

    # Merge the new column into the existing DataFrame
    merged_df = df.merge(source_df[[key_column, new_column_name]], on=key_column, how='left')

    return merged_df


@njit(parallel=True)
def _numba_mask(arrays, centers, margins):
    """
    Compute a boolean mask for rows where all values fall within [center - err, center + err].

    This Numba-compiled function runs in parallel (multi-threaded) across rows using prange.
    It stops checking a row as soon as one column is out-of-bound, avoiding unnecessary work.

    Parameters:
    -----------
    arrays : 2D np.ndarray
        Input data shaped (n_cols, n_rows), each row across columns is tested.
    centers : 1D np.ndarray
        Center values for each column (length = n_cols).
    margins : 1D np.ndarray
        Margins for each column (length = n_cols).

    Returns:
    --------
    mask : 1D np.ndarray of bool
        True for rows where all column values are within [center - err, center + err].
    """
    n_cols, n_rows = arrays.shape
    mask = np.ones(n_rows, dtype=np.bool_)
    for j in prange(n_rows):
        for i in range(n_cols):
            v = arrays[i, j]
            c = centers[i]; e = margins[i]
            if v < c - e or v > c + e:
                mask[j] = False
                break
    return mask


def filter_df(df, margins):
    """
    Filter DataFrame rows by column-wise margins.

    Parameters:
    -----------
    df : pandas.DataFrame
        Input dataframe containing numeric columns used in margins.
    margins : dict[str, list[float, float]]
        Mapping from column name to [center, error_margin].

    Returns:
    --------
    pandas.DataFrame
        Subset of `df` where each column `col` satisfies:
        center - error_margin <= value <= center + error_margin.

    Raises:
    -------
    KeyError
        If any column in `margins` is missing from `df`.
    """
    cols = list(margins)
    for c in cols:
        if c not in df.columns:
            raise KeyError(f"Column {c!r} not found in DataFrame.")
    centers = np.array([margins[c][0] for c in cols], dtype=float)
    errs = np.array([margins[c][1] for c in cols], dtype=float)
    arr = np.vstack([df[c].to_numpy() for c in cols])
    mask = _numba_mask(arr, centers, errs)
    return df.loc[mask].copy()


def find_closest_system(dfs, margins):
    """
    From multiple DataFrames, apply `filter_df` to each using `margins`, then find
    the one whose filtered DataFrame contains the row closest to the centers.

    Parameters
    ----------
    dfs : list[pd.DataFrame]]
        Candidate DataFrames to search.
    margins : dict[str, (center, err)]
        Columns and margin specs to filter by.

    Returns
    -------
    best_filtered_df : pd.DataFrame
        The filtered DataFrame whose best row is closest to the center vector.
    best_row : pd.Series
        The single best matching row.

    Raises
    ------
    ValueError
        If none of the DataFrames has any rows within the margins.
    """
    features = list(margins.keys())
    center_vec = np.array([margins[c][0] for c in features], dtype=float)

    best = {'df': None, 'filtered': None, 'row': pd.Series(dtype=float), 'dist': np.inf, 'orig_idx': None}

    for df in dfs:
        filtered = filter_df(df, margins)
        if filtered.empty:
            continue

        pts = filtered[features].to_numpy()

        mask = np.isfinite(pts).all(axis=1)
        if not mask.all():
            filtered = filtered.iloc[mask]
            pts = pts[mask]
        if pts.size == 0:
            continue

        tree = cKDTree(pts)
        dist, idx = tree.query(center_vec, k=1)

        if dist < best['dist']:
            orig_idx = filtered.index[idx]  # capture index in original df
            best.update({
                'df': df,
                'filtered': filtered,
                'row': df.loc[orig_idx],  # full row from original
                'dist': dist,
                'orig_idx': orig_idx
            })

    if best['df'] is None:
        raise ValueError("No match found with any system in the database for the given values.")

    return best['df'], best['filtered'], best['row']


def estimate_nova(dfs, margins):  
    best_estimation = find_closest_system(dfs, margins)
    df =  best_estimation[0]
    # filterd_df = best_estimation[1]
    closest_row = best_estimation[2]
    if not closest_row.empty:
        # find time and cycle number at the closest row:
        cycle = closest_row["cycle"]
        time = closest_row["time"]
    
        #  A dictionary where keys are cycles numbers and their values are lists containing the timing of their start and end 
        cycles_timing = demarcators.demarcate_nova_eruptions(df)
        return  time - cycles_timing[cycle][0]
    else:
        return -1