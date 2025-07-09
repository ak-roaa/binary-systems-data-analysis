import pandas as pd


def read_mat_file(file_name):
    """
    Reads a tabular data file and returns a DataFrame.

    Parameters
    ----------
    file_name : str
        The path to the data file.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the data from the file, with columns:
        'cycle', 'Macc', 'Menv', 'Mej', 'Yenv', 'Yej', 'Zenv', 'Zej',
        'Tmax', 'Tc', 'RHOc', 'time', 't3', 't-ML', 'C12', 'C13',
        'N14', 'N15', 'O16', 'O17', 'O18', 'Ne', 'Na', 'Mg',
        'Al26', 'Al27', 'Si', 'P', 'Vej_avg', 'Mdot_ej',
        'MWD', 'Iacc', 'Iej', 'Press'
    """
    df = pd.read_csv(file_name, sep=r"\s+", header=None, low_memory=False)
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.iloc[1:,]  # Skip the first row

    column_names = [
    "cycle", "Macc", "Menv", "Mej", "Yenv", "Yej", "Zenv", "Zej",
    "Tmax", "Tc", "RHOc", "time", "t3", "t-ML", "C12", "C13",
    "N14", "N15", "O16", "O17", "O18", "Ne", "Na", "Mg",
    "Al26", "Al27", "Si", "P", "Vej_avg", "Mdot_ej",
    "MWD", "Iacc", "Iej", "Press"
    ]
    df.columns = column_names
    return df


def concatenate_files(file_list):
    """
    Concatenates multiple data files into a single DataFrame.

    Parameters
    ----------
    file_list : list of str
        A list of paths to the data files.

    Returns
    -------
    pd.DataFrame
        A concatenated DataFrame containing data from all files.
    """
    dfs = []
    cycle_offset = 0
    time_offset = 0.0

    for file_name in file_list:
        df = read_mat_file(file_name)
        if cycle_offset or time_offset:
            df["cycle"] += cycle_offset
            df["time"] += time_offset
        cycle_offset = df["cycle"].max()
        time_offset = df["time"].max()
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)
