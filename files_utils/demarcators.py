import pandas as pd


def demarcate_decay_phases(df):
    """
    Identifies the start and end indices of the decay phase for each cycle.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame containing the system's data.

    Returns
    -------
    dict
        A dictionary where keys are cycle numbers and values are lists containing
        the start and end indices of the decay phase for each cycle.
    """
    result = {}
    max_cycle = df["cycle"].max()
    n = len(df)

    for cycle in range(1, max_cycle):
        cycle_df = df[df["cycle"] == cycle]
        if cycle_df.empty:
            continue

        first_idx = cycle_df.index[0]
        last_idx = cycle_df.index[-1]

        # Find delimiter_1: last negative value of accumulated mass, end of eruption
        delimiter_1 = first_idx
        subset = df.loc[first_idx:last_idx]
        ejecta_phase = subset[subset["accumulated mass"] < 0]
        if not ejecta_phase.empty:
            delimiter_1 = int(ejecta_phase.index[-1])
            

        # Find delimiter_2: first increase in effective temperature (located in the next cycle)
        delimiter_2 = last_idx
        for idx in range(last_idx + 1, n):
            if df.loc[idx, "effective temperature"] > df.loc[idx - 1, "effective temperature"]:
                delimiter_2 = idx
                break

        result[cycle] = [delimiter_1, delimiter_2]

    return result


def demarcate_nova_eruptions(df):
    """
    Identifies the start and end indices of the entire eruption phase for each cycle, includes a small
    phase of the next cycle that includes effective temperature decay.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame containing the system's data.

    Returns
    -------
    dict
        A dictionary where keys are cycle numbers and values are lists containing
        the start and end indices of the entire eruption phase for each cycle.
    """
    result = {}
    max_cycle = df["cycle"].max()

    for cycle in range(1, max_cycle):
        cycle_data = df[df["cycle"] == cycle]
        next_cycle_data = df[df["cycle"] == cycle+1]

        mask_ej = cycle_data["accumulated mass"] < 0
        mask_inc = next_cycle_data["effective temperature"] > next_cycle_data["effective temperature"].shift(1)

        delimiter_1 = cycle_data.loc[mask_ej].index[0] if mask_ej.any() else None
        delimiter_2 = next_cycle_data.loc[mask_inc].index[0] if mask_inc.any() else None

        result[cycle] = [delimiter_1, delimiter_2]

    return result


def demarcate_cycles(df):
    """
    For each cycle (an integer), return the first and last row index representing that cycle.
    """
    result = {}
    max_cycle = df["cycle"].max()
    for cycle in range(1, max_cycle+1):
        cycle_df = df[df["cycle"] == cycle]
        delimiter_1 = cycle_df.index[0]
        delimiter_2 = cycle_df.index[-1]
        result[cycle] = [delimiter_1, delimiter_2]
    return result
