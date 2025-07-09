import plotly.graph_objects as go
import numpy as np
import pandas as pd


def draw_cycles(df, cycles_list, demarcator_func):
    """
    Plots time-effective temperature curves for specified cycles using Plotly.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame containing the system's data.
    cycles_list : list of int
        A list of cycle numbers to plot.
    demarcator_func : function
        A function that returns a dictionary of {cycle_number: (start_idx, end_idx)}.

    Returns
    -------
    plotly.graph_objs._figure.Figure
        The Plotly figure object for Dash or standalone use.
    """
    cycles_dict = demarcator_func(df)

    fig = go.Figure()

    for cycle in cycles_list:
        delimiter_1, delimiter_2 = cycles_dict.get(cycle, (None, None))
        if delimiter_1 is None or delimiter_2 is None:
            continue  # Skip invalid cycles

        phase = df.iloc[delimiter_1:delimiter_2].copy()
        phase['time'] -= phase['time'].min()
        phase['time'] = np.log10(phase['time'] + 1e-10)  # Avoid log(0)

        fig.add_trace(
            go.Scatter(
                x=phase['time'],
                y=phase['effective temperature'],
                mode='markers',
                name=f"Cycle {cycle}"
            )
        )

    fig.update_layout(
        title="Time-Effective Temperature Curve",
        xaxis_title="Time (log scale)",
        yaxis_title="Effective Temperature (log K)",
        template="plotly_white",
        height=600,
        width=1000,
    )

    return fig


def calculate_cycles_length(df):
    """
    Calculate the duration of each cycle in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing these columns:
        - 'cycle': integer cycle identifiers
        - 'time': time in years

    Returns
    -------
    dict[int, pd.Timedelta]
        Dictionary mapping each cycle number to its length.
    """
    grp = df.groupby('cycle')['time']
    duration_series = grp.max().sub(grp.min())
    return duration_series.to_dict()


def draw_cycles_lengths_vs_t3(l_df, mat_df):
    """
    Plot cycle lengths (log10) on x-axis against t3 values on y-axis, excluding missing data.

    Args:
        l_df (pandas.DataFrame): Input data for cycles; passed into
            `calculate_cycles_length(l_df)` which returns a dict mapping cycle IDs to lengths.
        mat_df (pandas.DataFrame): DataFrame containing the `t3` column with values per cycle_id

    Returns:
        a plotly figure of t3 vs cycle_length (log10)
    """
    # Calculate cycle lengths
    cycles_lengths = calculate_cycles_length(l_df)

    # Prepare t3 series indexed by cycle_id
    t3_series = mat_df.set_index("cycle_id")["t3"] if "cycle_id" in mat_df.columns else mat_df["t3"]

    # Filter out cycles with missing data
    valid_cycles = [
        cid for cid in cycles_lengths
        if cid in t3_series.index and pd.notna(cycles_lengths[cid]) and pd.notna(t3_series[cid])
    ]
    valid_lengths = [cycles_lengths[cid] for cid in valid_cycles]
    valid_t3 = [t3_series.loc[cid] for cid in valid_cycles]
    valid_t3 = np.log10(valid_t3)

    # Apply log10 transformation to cycle lengths
    log_lengths = np.log10(valid_lengths)

    # Build Plotly figure with log_lengths on x-axis, t3 on y-axis
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=log_lengths, y=valid_t3,
        mode="markers+lines",
        name="t3 vs Cycle Length (log10)",
        marker=dict(color="blue"),
        text=valid_cycles,  # cycle_id on hover
        hovertemplate="Cycle ID: %{text}<br>Cycle Length (log10): %{x}<br>t3: %{y}<extra></extra>"
    ))

    fig.update_layout(
        title="t3 vs Cycle Length (log10)",
        xaxis=dict(title="Cycle Length (log10)"),
        yaxis=dict(title="t3"),
        legend=dict(x=0.01, y=0.99)
    )

    return fig



