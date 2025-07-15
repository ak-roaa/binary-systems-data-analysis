import plotly.graph_objects as go
import numpy as np
import pandas as pd


def system_info(df):
    """
    Extracts basic metadata and structural information from a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame.

    Returns
    -------
    dict
        A dictionary containing:
            - 'column_names': List of column names.
            - 'num_columns': Total number of columns.
            - 'num_rows': Total number of rows.
            - 'max_cycle': Maximum value in 'cycle' column if present, else None.
    """
    result = {
        'column_names': df.columns.tolist(),
        'num_columns': df.shape[1],
        'num_rows': df.shape[0],
        'max_cycle': df['cycle'].max() if 'cycle' in df.columns else None
    }

    return result


def get_df_preview(df, columns_to_show=None, row_start=None, row_end=None):
    """
    Returns a preview of a DataFrame with specified columns and row slice.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame.
    columns_to_show : list of str, optional
        List of column names to include. If None, all columns are included.
    row_start : int, optional
        Starting row index (inclusive). Defaults to 0 if None.
    row_end : int, optional
        Ending row index (exclusive). Defaults to end of DataFrame if None.

    Returns
    -------
    pandas.DataFrame
        A subset of the DataFrame with selected columns and rows.
    """
    if columns_to_show is not None:
        columns_to_show = [col for col in columns_to_show if col in df.columns]
        df = df[columns_to_show]

    return df.iloc[row_start:row_end]


def plot_x_vs_y(df, x_column, y_column, log_x=False, log_y=False):
    """
    Creates a scatter plot of two columns in a DataFrame using Plotly,
    with optional log10 transformation for each axis.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame.
    x_column : str
        Column name for the x-axis.
    y_column : str
        Column name for the y-axis.
    log_x : bool, default False
        If True, apply log10 transformation to the x-axis values.
    log_y : bool, default False
        If True, apply log10 transformation to the y-axis values.

    Returns
    -------
    plotly.graph_objects.Figure
        A Plotly Figure object representing the scatter plot.
    """
    if x_column not in df.columns or y_column not in df.columns:
        raise ValueError(f"Columns '{x_column}' and/or '{y_column}' not found in DataFrame.")

    x = df[x_column]
    y = df[y_column]

    if log_x:
        x = x[x > 0]
        y = y.loc[x.index]
        x = np.log10(x)

    if log_y:
        y = y[y > 0]
        x = x.loc[y.index]
        y = np.log10(y)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(size=8, color='royalblue'),
        name=f'{y_column} vs {x_column}'
    ))

    fig.update_layout(
        title=f"{'log10 ' if log_y else ''}{y_column} vs {'log10 ' if log_x else ''}{x_column}",
        xaxis_title=f"log10({x_column})" if log_x else x_column,
        yaxis_title=f"log10({y_column})" if log_y else y_column,
        template="plotly_white"
    )

    return fig


def calculate_cycles_length(df):
    """
    Calculates the length (duration) of each cycle from a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing:
            - 'cycle': Cycle ID (grouping key)
            - 'time': Time values for each entry (in years)

    Returns
    -------
    dict[int, float]
        Dictionary mapping each cycle ID to its duration (max - min time).
    """
    grp = df.groupby('cycle')['time']
    duration_series = grp.max() - grp.min()
    return duration_series.to_dict()


def plot_cycles_lengths_vs_param(l_df, mat_df, param, log_x=False, log_y=False):
    """
    Plots a scatter plot of cycle lengths vs. a selected parameter (e.g., t3),
    with optional log scaling for both axes.

    Parameters
    ----------
    l_df : pandas.DataFrame
        DataFrame used to calculate cycle lengths.
    mat_df : pandas.DataFrame
        DataFrame containing the target parameter column.
    param : str
        Column name in mat_df to use on the x-axis.
    log_x : bool, default False
        If True, log10-transform the param values.
    log_y : bool, default False
        If True, log10-transform the cycle lengths.

    Returns
    -------
    plotly.graph_objects.Figure
        A Plotly scatter plot of the parameter vs. cycle length.
    """
    cycle_lengths = calculate_cycles_length(l_df)

    if "cycle" not in mat_df.columns:
        raise ValueError("'mat_df' must contain a 'cycle' column.")
    if param not in mat_df.columns:
        raise ValueError(f"'{param}' not found in 'mat_df'.")

    param_series = mat_df.set_index("cycle")[param]

    # Filter valid cycles
    valid_data = {
        cid: (cycle_lengths[cid], param_series[cid])
        for cid in cycle_lengths
        if cid in param_series.index and pd.notna(cycle_lengths[cid]) and pd.notna(param_series[cid])
    }

    if not valid_data:
        raise ValueError("No valid cycle data to plot.")

    x = pd.Series({cid: val[1] for cid, val in valid_data.items()})
    y = pd.Series({cid: val[0] for cid, val in valid_data.items()})

    if log_x:
        x = x[x > 0]
        y = y.loc[x.index]
        x = np.log10(x)

    if log_y:
        y = y[y > 0]
        x = x.loc[y.index]
        y = np.log10(y)

    x_label = f"{param} (log10)" if log_x else param
    y_label = "Cycle Length (log10)" if log_y else "Cycle Length"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x.values,
        y=y.values,
        mode="markers",
        name=f"{param} vs Cycle Length",
        marker=dict(color="blue"),
        text=x.index.astype(str),
        hovertemplate=(
            "Cycle: %{text}<br>"
            f"{x_label}: %{x}<br>"
            f"{y_label}: %{y}<extra></extra>"
        )
    ))

    fig.update_layout(
        title=f"{x_label} vs {y_label}",
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label),
        legend=dict(x=0.01, y=0.99)
    )

    return fig


def add_columns_to_df(df, source_file, key_column, column_indices_to_add, sheet_name=None):
    """
    Adds columns from an external CSV or Excel file to a DataFrame,
    using a shared key column for merging.

    Parameters
    ----------
    df : pandas.DataFrame
        The base DataFrame to which columns will be added.
    source_file : str
        Path to the source file (.csv or .xlsx).
    key_column : str
        Column in `df` to match with the row index of the source file.
    column_indices_to_add : list of int
        Indices of columns to import from the source file.
    sheet_name : str, optional
        Sheet name to use if the file is an Excel workbook.

    Returns
    -------
    pandas.DataFrame
        The original DataFrame with new columns added.
    """
    source_df = pd.read_excel(source_file, sheet_name=sheet_name) \
        if source_file.endswith(('.xls', '.xlsx')) else pd.read_csv(source_file)
    source_df.index = source_df.reset_index().index + 1  # Ensure numeric index starting at 1

    all_columns = list(source_df.columns)
    selected_columns = [
        all_columns[i] for i in column_indices_to_add
        if 0 <= i < len(all_columns) and all_columns[i] not in df.columns
    ]

    if not selected_columns:
        return df

    source_subset = source_df[selected_columns]
    merged_df = df.merge(source_subset, how='left', left_on=key_column, right_index=True)

    return merged_df


def plot_cycles(df, cycles_list, demarcator_func):
    """
    Plots the time vs effective temperature for specified cycles.

    Parameters
    ----------
    df : pandas.DataFrame
        Input data with time and effective temperature columns.
    cycles_list : list of int
        List of cycle numbers to plot.
    demarcator_func : callable
        Function that takes `df` and returns a dict mapping cycle numbers
        to (start_index, end_index) tuples.

    Returns
    -------
    plotly.graph_objects.Figure
        A Plotly scatter plot of effective temperature over time per cycle.
    """
    cycles_dict = demarcator_func(df)
    fig = go.Figure()

    for cycle in cycles_list:
        start_idx, end_idx = cycles_dict.get(cycle, (None, None))
        if start_idx is None or end_idx is None:
            continue

        phase = df.iloc[start_idx:end_idx].copy()
        phase['time'] -= phase['time'].min()
        phase['time'] = np.log10(phase['time'] + 1e-10)  # Prevent log(0)

        fig.add_trace(go.Scatter(
            x=phase['time'],
            y=phase['effective temperature'],
            mode='markers',
            name=f"Cycle {cycle}"
        ))

    fig.update_layout(
        title="Time vs Effective Temperature",
        xaxis_title="Time (log scale)",
        yaxis_title="Effective Temperature (log K)",
        template="plotly_white",
        height=600,
        width=1000,
    )

    return fig


"""
if __name__ == "__main__":
    df = read_l.concatenate_files(["l_045_025_A", "l_044_019_B"])
    df = add_columns_to_df(df, "MWD_MRD.xlsx", "cycle", [0, 1], "045_025")
    # get_df_preview(df,["cycle", "time", "MWD", "MRD", "effective temperature"])
    # fig = plot_x_vs_y(df, "time", "effective temperature", log_x=True)
    print(system_info(df))
"""