import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from files_utils import read_l, read_mat, estimators
# import db_calls


def build_df_for_estimations(l_files, mat_files, system_path, masses_df):
    """
    Construct two pandas DataFrames by reading and concatenating files for 'l' and 'mat'.

    Parameters
    ----------
    l_file : str
        Filename (relative to `system_path`) for the 'l' dataset.
    mat_file : str
        Filename (relative to `system_path`) for the 'mat' dataset.
    system_path : str
        Directory path where the data files are located. This path will be prepended to each
        filename in `l_file` and `mat_file`.
    relevant_columns : list of str
        List of column names to retain in the final merged DataFrame.
    masses_file : str
        The source file name to be used in the `add_column_to_df` function.
    sheet_name : str
        The sheet name to be used in the `add_column_to_df` function.
    comp_mass_column: str
        the column that has the values of the mass of the companion object    

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the merged data from 'l' and 'mat', with only the relevant columns.
    """
    # Construct full file paths
    full_path_l_files = [os.path.join(system_path, f) for f in l_files]
    full_path_mat_files =[os.path.join(system_path, f) for f in mat_files]

    try:
        # Read and concatenate 'l' and 'mat' files
        l_df = read_l.concatenate_files(full_path_l_files)
        mat_df = read_mat.concatenate_files(full_path_mat_files)
    except Exception as e:
        raise RuntimeError(f"Error reading files: {e}")

    try:
        # Add companion mass column to 'mat_df'
        mat_df = mat_df.drop(columns=['MWD'])
        mat_df = mat_df.drop(columns=['time'])
        mat_df_with_comp_mass = pd.merge(mat_df, masses_df, on='cycle', how='left')
    except KeyError as e:
        raise KeyError(f"Merging the companion mass column into the MAT file failed!': {e}")
    except Exception as e:
        raise RuntimeError(f"Error adding companion mass column: {e}")

    try:
        # Merge 'l_df' and 'mat_df_with_comp_mass' on 'cycle' column
        merged = pd.merge(l_df, mat_df_with_comp_mass, on='cycle', how='left')
    except KeyError as e:
        raise KeyError(f"Merge key error: {e}")
    except ValueError as e:
        raise ValueError(f"Value error during merge: {e}")
    except Exception as e:
        raise RuntimeError(f"Error merging DataFrames: {e}")

    # Select only the relevant columns
    comp_mass_column = masses_df.columns[2]
    relevant_columns = ["cycle", "time", "accumulated mass", "effective temperature",  "MWD", comp_mass_column]
    selected = [c for c in relevant_columns if c in merged.columns]
    if not selected:
        raise ValueError("None of the relevant columns are present in the merged DataFrame.")

    return merged.loc[:, selected].copy()


def check_sheet_in_files(file_name, folder_path):
    base_name = os.path.splitext(file_name)[0]
    for fname in os.listdir(folder_path):
        if fname.endswith(('.xlsx', '.xls')):
            path = os.path.join(folder_path, fname)
            try:
                xl = pd.ExcelFile(path)
                if base_name in xl.sheet_names:
                    # ✅ Sheet exists — load into a DataFrame and return it
                    df = pd.read_excel(path, sheet_name=base_name, engine="openpyxl")
                    return df  # returns the DataFrame
            except Exception as e:
                print(f"Error reading {fname}: {e}")
    return  pd.DataFrame()  # if nothing matches 


def retreive_systems_with_companion_mass(systems_db, masses_folder_path, systems_path):
    dfs_with_masses = []
    # systems_db is a dictionary of elements of the form system_name:[lst_files_l, lst_files_mat]
    for system_name in systems_db:
        system_path = os.path.join(systems_path, system_name)
        masses_df = check_sheet_in_files(system_name, masses_folder_path)
        if len(masses_df) != 0:
            # then there is info about the mass of the companion object
            cycles_nums = range(1,len(masses_df)+1)
            masses_df.insert(loc=0, column='cycle', value=cycles_nums)
            df = build_df_for_estimations(systems_db[system_name][0], systems_db[system_name][1], system_path, masses_df)
            dfs_with_masses.append(df)
    return dfs_with_masses



"""
if __name__ == '__main__':
    data_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "mat_l_data"))
    systems_db = db_calls.inspect_db(data_folder_path)
    dfs = retreive_systems_with_companion_mass(systems_db, "wd_comp_mass", data_folder_path)

    #  margins : dict[str, list[float, float]] Mapping from column name to [center, error_margin].
    margins = {"MWD": [0.699984, 0.01], "MRD": [0.449964,0.01]}
    res = estimators.estimate_nova(dfs, margins)
    print(res)
"""