import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from files_utils import read_l, read_mat, estimators


def build_df_for_estimations(l_df, mat_df, system_path):
    """
    Construct two DataFrames for 'l' and 'mat' files.

    Parameters
    ----------
    l_file : str
        Filename (relative to `system_path`) for the 'l' dataset.
    mat_file : str
        Filename (relative to `system_path`) for the 'mat' dataset.
    system_path : str
        Directory path where the data files are located. This path will be prepended to each
        filename in `l_file` and `mat_file`.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the merged data from 'l' and 'mat', with only the relevant columns for the temp decay analysis.
    """
    try:
        # Merge 'l_df' and 'mat_df' on 'cycle' column
        merged = pd.merge(l_df, mat_df, on='cycle', how='left')
    except KeyError as e:
        raise KeyError(f"Merge key error: {e}")
    except ValueError as e:
        raise ValueError(f"Value error during merge: {e}")
    except Exception as e:
        raise RuntimeError(f"Error merging DataFrames: {e}")

    # Select only the relevant columns
    relevant_columns = ["cycle", "time", "accumulated mass", "effective temperature",  "MWD", "companion_mass"]
    selected = [c for c in relevant_columns if c in merged.columns]
    if not selected:
        raise ValueError("The relevant columns for the estimation are not all present in the DataFrame.")

    return merged.loc[:, selected].copy()
