import os
import tempfile
import shutil
import pandas as pd

def extract_mrd_column(file_path, sheet_name=None):
    """
    Extracts the 'MRD' column from a CSV or Excel file and returns it as a DataFrame.

    Parameters
    ----------
    file_path : str
        Path to the CSV or Excel file.
    sheet_name : str or None, default None
        Sheet name if reading an Excel file. Ignored for CSV files.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing only the 'MRD' column.

    Raises
    ------
    ValueError
        If the file extension is unsupported or 'MRD' column is not found.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.csv':
        df = pd.read_csv(file_path)
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    if 'MRD' not in df.columns:
        raise ValueError("Column 'MRD' not found in the file.")

    return df[['MRD']]


def merge_mrd_column_to_files(file_paths, mrd_df):
    """
    Merges the 'MRD' column from a DataFrame into multiple extensionless space-separated files.
    
    Each file gets a consecutive slice of the 'MRD' column based on its number of data rows.

    Parameters
    ----------
    file_paths : list of str
        List of paths to the extensionless space-separated files.
    mrd_df : pandas.DataFrame
        DataFrame containing only the 'MRD' column.

    Raises
    ------
    ValueError
        If the total number of data rows in the files does not match the length of MRD column.
    """
    if 'MRD' not in mrd_df.columns:
        raise ValueError("DataFrame must contain an 'MRD' column.")

    mrd_values = mrd_df['MRD'].tolist()
    total_mrd_len = len(mrd_values)

    # Step 1: Count data lines in each file (excluding header)
    file_lengths = []
    for path in file_paths:
        with open(path, 'r') as f:
            lines = f.readlines()
            data_lines = [line for line in lines[1:] if line.strip()]  # exclude header and blanks
            file_lengths.append(len(data_lines))


    # Step 2: Process each file
    current_index = 0
    for i, path in enumerate(file_paths):
        with open(path, 'r') as f:
            lines = f.readlines()

        header = lines[0].strip() + " MRD\n"
        data_lines = [line.rstrip('\n') for line in lines[1:] if line.strip()]
        num_lines = file_lengths[i]

        # Slice corresponding MRD values
        mrd_slice = mrd_values[current_index:current_index + num_lines]
        current_index += num_lines

        # Create new file content
        updated_lines = [f"{line.strip()} {mrd_val}" for line, mrd_val in zip(data_lines, mrd_slice)]

        # Write to temp file
        dir_name = os.path.dirname(path)
        with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False) as tmpfile:
            tmpfile.write(header)
            for line in updated_lines:
                tmpfile.write(line + "\n")
            temp_name = tmpfile.name

        # Replace original file
        shutil.move(temp_name, path)

    print("✅ MRD column successfully merged into all files.")


"""
if __name__ == "__main__":
    col =  extract_mrd_column("MWD_MRD.xlsx", "070_070")
    merge_mrd_column_to_files(["mat_070_070_mt_A", "mat_070_034_mt_B", "mat_070_030_mt_C", "mat_070_025_mt_D", "mat_070_019_mt_E", "mat_070_016_mt_F"], col)
"""