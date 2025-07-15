import dash
from dash import dash_table
import pandas as pd
from dash import dcc, html
from dash import ctx
from dash.dependencies import Input, Output, State
import os
import shutil
import base64
import plotly.graph_objs as go
import ast  # For safely evaluating the list input

from pages_layouts.home_page import home_page
from pages_layouts.db_page import db_page
from pages_layouts.data_analysis_page import data_analysis_page
from pages_layouts.explore_system_page import explore_system_page
from pages_layouts.advanced_search_page import advanced_search_page


from callbacks_helpers import db_calls, estimators_calls
from files_utils import system_functions, demarcators, read_l, read_mat, estimators


#############################   Global Variables  #############################
systems_db = {}
data_folder_path = ""
current_system_df_l = None
current_system_df_mat = None


#############################   Main Layout  #############################
# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Binary Stars Data Analysis"


# Define the layout of the navigation bar
navbar_layout = html.Div([
    dcc.Link('Homepage', href='/', className='nav-link'),
    dcc.Link('Database', href='/db', className='nav-link'),
    dcc.Link('Explore System', href='/explore_system', className='nav-link'),
    dcc.Link('Data Analysis', href='/analysis', className='nav-link'),
    dcc.Link('Advanced Search', href='/advanced_search', className='nav-link'),
], className='navbar')


# Define the main layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1("Binary Stars Data Analysis", className='main-header'),
    navbar_layout,
    html.Div(id='page-content')
])


@app.callback(
    Output('page-content', 'children'), 
    Input('url', 'pathname')
)
def display_page(pathname):
    """Dynamically displays content based on the URL path."""
    if pathname == '/db': return db_page
    elif pathname == '/analysis': return data_analysis_page
    elif pathname == '/explore_system': return explore_system_page
    elif pathname == '/advanced_search': return advanced_search_page
    else: 
        return home_page


#############################   Database Page   #############################
@app.callback(
    Output('systems-list-output', 'children'), 
    Input('load-systems-button', 'n_clicks')
)
def show_systems_in_db(n_clicks):
    """Displays the names of systems in the database."""
    if not n_clicks:
        return "Load the names of binary systems that are in the database"
    
    try:
        if not systems_db:
            return html.P("The database is empty.", className='info-message')
        system_elements = []
        for sys_name, sys_files in sorted(systems_db.items()):
            system_card = html.Div([html.H4(f"System: {sys_name}")])
            system_elements.append(system_card)
        return html.Div(system_elements)
    
    except Exception as e:
        return html.P(f"Error loading systems: {str(e)}", className='error-message')


@app.callback(
    Output("system-upload-output", "children"),
    Input("system-upload-button", "n_clicks"),
    State("system-name-input", "value"),
    State("input-files", "contents"),
    State("input-files", "filename")
)
def add_system_db(n_clicks, system_name, contents, filenames):
    global systems_db
    if not n_clicks:
        return ""
    if not system_name:
        return html.Div("⚠️ Please enter a system name.")
    if system_name in systems_db:
        return html.Div("⚠️ System already in the database.")
    if not contents or not filenames:
        return html.Div("⚠️ No files uploaded.")

    # Normalize to list
    if isinstance(contents, str):
        contents = [contents]
    if isinstance(filenames, str):
        filenames = [filenames]

    decoded_files = []
    for content, filename in zip(contents, filenames):
        try:
            header, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            decoded_files.append({"filename": filename, "content": decoded})
        except Exception as e:
            return html.Div(f"⚠️ Error decoding {filename}: {e}")

    try:
        db_calls.add_system(data_folder_path, system_name, decoded_files)
    except Exception as e:
        return html.Div(f"❌ Error in add_system: {e}")

    systems_db = db_calls.inspect_db(data_folder_path)
    return html.Div(f"✅ files: {[file['filename'] for file in decoded_files]} added to system '{system_name}'.")


@app.callback(
    Output("update-existing-system-output", "children", allow_duplicate=True),
    Input("add-file-button", "n_clicks"),
    State("uploaded-file", "contents"),
    State("uploaded-file", "filename"),
    State("existing-system-id", "value"),
    State("file-name", "value"),
    prevent_initial_call=True
)
def add_file_db(n_clicks, contents, filenames, system_name, file_name):
    global systems_db
    if not contents:
        return html.Div("⚠️ No files selected.")
    if not system_name:
        return html.Div("⚠️ Please enter a system name.")
    if system_name not in systems_db:
        return html.Div(f"⚠️ System '{system_name}' not found.")
    if not file_name:
        return html.Div("⚠️ Please enter a filename.")
    
    if isinstance(contents, str):
        contents = [contents]
        filenames = [filenames]

    messages = []
    for content, filename in zip(contents, filenames):
        if filename == file_name:
            try:
                _, content_string = content.split(',', 1)
                decoded = base64.b64decode(content_string)
                db_calls.add_file_to_system(data_folder_path, system_name, filename, decoded)
                messages.append(f"✅ {filename} saved to '{system_name}'.")
            except Exception as e:
                messages.append(f"❌ {filename}: Error saving ({e})")
        else:
            messages.append(f"⚠️ {filename}: Filename does not match '{file_name}'.")

    systems_db = db_calls.inspect_db(data_folder_path)
    return html.Ul([
        html.Li(msg) for msg in messages
    ])


@app.callback(
    Output("update-existing-system-output", "children", allow_duplicate=True),
    Input("delete-file-button", "n_clicks"),
    State("existing-system-id", "value"),
    State("file-name", "value"),
    prevent_initial_call=True
)
def delete_file_db(n_clicks, system_name, file_name):
    global systems_db
    if not system_name:
        return html.Div("⚠️ Please enter a system name.")
    if system_name not in systems_db:
        return html.Div(f"⚠️ System '{system_name}' not found.")
    if not file_name:
        return html.Div("⚠️ Please enter a filename.")

    try:
        db_calls.delete_file_from_system(data_folder_path, system_name, file_name)
        systems_db = db_calls.inspect_db(data_folder_path)
        return html.Div(f"✅ {file_name} deleted from '{system_name}'.")
    except FileNotFoundError:
        return html.Div(f"❌ {file_name}: File not found in '{system_name}'.")
    except Exception as e:
        return html.Div(f"❌ {file_name}: Error deleting ({e})")


@app.callback(
    Output("update-existing-system-output", "children", allow_duplicate=True),
    Input("delete-system-button", "n_clicks"),
    State("existing-system-id", "value"),
    prevent_initial_call=True
)
def delete_system_db(n_clicks, system_name):
    global systems_db
    if not system_name:
        return html.Div("⚠️ Please enter a system name.")  
    system_path = os.path.join(data_folder_path, system_name)
    if not os.path.exists(system_path):
        return html.Div(f"⚠️ System '{system_name}' not found.")
    
    try:
        # Delete the system directory and its contents
        shutil.rmtree(system_path)
        systems_db = db_calls.inspect_db(data_folder_path)
        return html.Div(f"✅ System '{system_name}' and its files have been deleted.")
    except Exception as e:
        return html.Div(f"❌ Error deleting system '{system_name}': {e}")


#############################   Explore System Page   #######################
@app.callback(
    Output('system-name-dropdown', 'options'),
    Input('url', 'pathname')
)
def populate_dropdown_systems_names(n_clicks):
    return [{'label': name, 'value': name} for name in systems_db.keys()]


@app.callback([Output('files-list-to_display', 'children'), Output('system-info-output', 'children'), Output('cycle-length-col-dropdown', 'options')],
    [Input('load-button', 'n_clicks')],
    [State('system-name-dropdown', 'value')],
    prevent_initial_call=True
)
def enter_system_to_explore(n_clicks, system_name):
    if not n_clicks or not system_name:
        return "", ""

    # Get file names
    system_files = systems_db.get(system_name, [])
    system_files_flat = sum(system_files, [])

    file_list = html.Div([
        html.H4("System Files:"),
        html.Ul([html.Li(f) for f in system_files_flat])
    ])

    system_path = os.path.join(data_folder_path, system_name)

    l_files = [os.path.join(system_path, f) for f in system_files[0]]
    mat_files = [os.path.join(system_path, f) for f in system_files[1]]

    system_df_l = read_l.concatenate_files(l_files)
    system_df_mat = read_mat.concatenate_files(mat_files)
    merged_df = pd.merge(system_df_l, system_df_mat, on='cycle', how='outer')
    
    global current_system_df_l
    global current_system_df_mat
    current_system_df_l = system_df_l
    current_system_df_mat = system_df_mat

    # Get system info
    info = system_functions.system_info(merged_df)

    info_display = html.Div([
        html.H4("System Information:"),
        html.Ul([
            html.Li(f"Number of Rows: {info['num_rows']}"),
            html.Li(f"Number of Columns: {info['num_columns']}"),
            html.Li(f"Number of Cycles: {info['max_cycle']}")
        ])
    ])

    cycle_len_plot_cols = [{'label': col, 'value': col} for col in current_system_df_mat.columns]
    return (file_list, info_display, cycle_len_plot_cols)


@app.callback(
    Output('df-column-selector', 'options'),
    Input('df-selector-display-table', 'value'),
    prevent_initial_call=True
)
def get_df_columns(file_type):
    current_df = get_df_type(file_type)
    return [{'label': col, 'value': col} for col in current_df.columns]


def get_df_type(file_type):
    if file_type == 'L':
        return current_system_df_l
    elif file_type == 'MAT':
        return current_system_df_mat
    return pd.merge(current_system_df_l, current_system_df_mat, on='cycle', how='outer')


@app.callback(
    Output('df-output', 'children'),
    Input('show-df-button', 'n_clicks'),
    State('df-column-selector', 'value'),
    State('df-selector-display-table', 'value'),
    State('row-start', 'value'),
    State('row-end', 'value'),
    prevent_initial_call=True
)
def update_table(n_clicks, selected_columns, file_type, row_start, row_end):
    if n_clicks == 0 or not file_type:
        return ""

    current_df = get_df_type(file_type)
    
    # get the df
    preview_df = system_functions.get_df_preview(current_df, selected_columns, row_start=row_start, row_end=row_end)

    # Return as a Dash DataTable for display
    return dash_table.DataTable(
        data=preview_df.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in preview_df.columns],
        page_size=10,
        sort_action='native',
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
    )


@app.callback(
    [Output('plot-col1', 'options'), Output('plot-col2', 'options')],
    Input('df-selector-plot', 'value'),
    prevent_initial_call=True
)
def get_plot_columns(file_type):
    current_df = get_df_type(file_type)
    options = [{'label': col, 'value': col} for col in current_df.columns]
    return options, options


@app.callback(
    Output('plot-output', 'children'),
    Input('plot-button', 'n_clicks'),
    State('df-selector-plot', 'value'),
    State('plot-col1', 'value'),
    State('plot-col2', 'value'),
    State('log-scale-col1', 'value'),
    State('log-scale-col2', 'value'),
    prevent_initial_call=True
)
def plot_2_params(n_clicks, file_type, col1, col2, log1, log2):
    if col1 is None or col2 is None:
        return html.Div("Please select both columns.", className='warning-message')

    # Determine if log scaling is requested
    log_x = 'log' in log1 if log1 else False
    log_y = 'log' in log2 if log2 else False

    try:
        df = get_df_type(file_type)
        fig = system_functions.plot_x_vs_y(df, col1, col2, log_x=log_x, log_y=log_y)
        return dcc.Graph(figure=fig)
    except Exception as e:
        return html.Div(f"Error generating plot: {str(e)}", className='error-message')


@app.callback(
    Output('plot-cycle-length-output', 'children'),
    Input('plot-cycle-length-button', 'n_clicks'),
    State('cycle-length-col-dropdown', 'value'),
    State('log-scale-checklist', 'value'),
    prevent_initial_call=True
)
def cycle_length_vs_col_plot(n_clicks, selected_column, log_scale_values):
    if not n_clicks or not selected_column:
        return html.Div("Please select a column and click Plot.")

    # Determine if log scaling is requested
    log_x = 'log_x' in log_scale_values
    log_y = 'log_y' in log_scale_values  
    
    # Create the figure
    try:
        fig =  system_functions.plot_cycles_lengths_vs_param(current_system_df_l, current_system_df_mat, selected_column, log_x, log_y)
        return dcc.Graph(figure=fig)
    except Exception as e:
        return html.Div(f"Error generating plot: {str(e)}", className='error-message')


############################  Data Analysis Page   ####################
@app.callback(
    Output('temp-time-plot', 'children'),
    Input('generate-temp-time-plot-button', 'n_clicks'),
    State('system-name-input-temp-time', 'value'),
    State('cycles-list-input-temp-time', 'value')
)
def plot_effective_temperature_vs_time(n_clicks, system_name, cycles_list_str):
    if n_clicks == 0 or not system_name or not cycles_list_str:
        return html.Div("Please enter the system name and the list of cycles to plot.")

    try:
        # convert the cycles list from an input string to a list
        cycles_list = ast.literal_eval(cycles_list_str)
        if not isinstance(cycles_list, list):
            raise ValueError
    except Exception:
        return html.Div("Invalid cycles list format. Use [10, 100, 200]")

    files_lst = systems_db[system_name][0]
    system_path = os.path.join(data_folder_path, system_name)
    files_lst = [os.path.join(system_path, f) for f in files_lst]
    system = read_l.concatenate_files(files_lst)

    # Call plot function
    try:
        fig = system_functions.plot_cycles(system , cycles_list, demarcators.demarcate_decay_phases)
        return dcc.Graph(figure=fig)
    except Exception as e:
        return html.Div(f"Error generating time-temp plot: {str(e)}", className='error-message')

#############################   Estimate Page   #######################
@app.callback(
    Output('last-nova-output', 'children'),
    Input('estimate-nova-button', 'n_clicks'),
    State('wd-mass-input', 'value'), State('wd-mass-delta-input', 'value'),
    State('comp-mass-input', 'value'), State('comp-mass-delta-input', 'value'),
    State('eff-temp-input', 'value'), State('eff-temp-delta-input', 'value'),
    prevent_initial_call=True
)
def estimate_last_nova_callback(n_clicks, wd_mass, wd_mass_delta, comp_mass, comp_mass_delta, eff_temp, eff_temp_delta):
    # Ensure all inputs are present
    if any(v is None for v in [wd_mass, wd_mass_delta, comp_mass, comp_mass_delta, eff_temp, eff_temp_delta]):
        return html.P("Please fill in all input fields (including deltas).", className='error-message')

    # Make margin dict from user inputs
    margins = {'MWD': [wd_mass, wd_mass_delta], 'MRD': [comp_mass, comp_mass_delta], 'effective temperature': [eff_temp, eff_temp_delta]}

    dfs = estimators_calls.retrieve_systems_with_companion_mass(systems_db, "masses_data", data_folder_path)
    time = estimators.estimate_nova(dfs, margins)

    if time == -1:
        return html.P("No match found.", className='error-message')

    return html.Div([
        html.P(f"Last nova estimated {time:.3f} years ago", className='success-message')
    ])


@app.callback(
    Output('fourth-param-output', 'children'),
    Input('estimte-fourth-param-button', 'n_clicks'),
    State('param1-dropdown', 'value'), State('param1-value', 'value'), State('param1-delta', 'value'),
    State('param2-dropdown', 'value'), State('param2-value', 'value'), State('param2-delta', 'value'),
    State('param3-dropdown', 'value'), State('param3-value', 'value'), State('param3-delta', 'value'),
    prevent_initial_call=True
)
def estimate_one_missing_parameter_callback(n_clicks, p1n, p1v, p1d, p2n, p2v, p2d, p3n, p3v, p3d):
    # Ensure three selections with values/deltas
    inputs = [(p1n, p1v, p1d), (p2n, p2v, p2d), (p3n, p3v, p3d)]
    if any(name is None or val is None or delta is None for name, val, delta in inputs):
        return html.P("Please select three parameters and enter all values & deltas.", className='error-message')

    # Check uniqueness of parameter names
    names = {p1n, p2n, p3n}
    if len(names) != 3:
        return html.P("Please select three *unique* parameters.", className='error-message')

    # Build margins dict
    margins = {name: [val, delta] for name, val, delta in inputs}

    # Determine the missing 4th parameter
    all_params = {"MWD", "MRD", "time", "effective temperature"}
    missing = (all_params - names)
    print(missing)
    if len(missing) != 1:
        return html.P("Internal error: could not identify missing parameter.", className='error-message')
    missing_param = missing.pop()

    # Call estimation logic
    dfs = estimators_calls.retrieve_systems_with_companion_mass(systems_db, "masses_data", data_folder_path)
    estimate = estimators.find_closest_system_parallel(dfs, margins, max_workers)
    closest_row = estimate[2]
    if closest_row.empty:
        return html.P("No system found within the given tolerances.", className='error-message')
    estimated_value = closest_row[missing_param]
    return html.P(f"Estimated {missing_param}: {estimated_value:.3f}", className='success-message')


@app.callback(
    Output('estimated-two-params-output', 'children'),
    Input('estimate-two-params-button', 'n_clicks'),
    State('param1-two-dropdown', 'value'), State('param1-two-value', 'value'), State('param1-two-delta', 'value'),
    State('param2-two-dropdown', 'value'), State('param2-two-value', 'value'), State('param2-two-delta', 'value'),
    prevent_initial_call=True
)
def estimate_two_parameters_callback(n_clicks, p1n, p1v, p1d, p2n, p2v, p2d):
    try:
        # Validate input presence
        inputs = [(p1n, p1v, p1d), (p2n, p2v, p2d)]
        if any(name is None or val is None or delta is None for name, val, delta in inputs):
            return html.P("Please select two parameters and enter all values & deltas.", className='error-message')

        # Check that parameters are unique
        names = {p1n, p2n}
        if len(names) != 2:
            return html.P("Please select two *unique* parameters.", className='error-message')

        # Build margins dictionary
        margins = {p1n: [p1v, p1d], p2n: [p2v, p2d]}

        # Load system data
        dfs = estimators_calls.retrieve_systems_with_companion_mass(systems_db, "masses_data", data_folder_path)
        if dfs is None or dfs.empty:
            return html.P("No system data found. Please check the data source.", className='error-message')

        # Run filtering logic
        matching_systems = estimators.find_closest_system_parallel(dfs, margins, max_workers=4)
        if matching_systems.empty:
            return html.P("No systems found within the given parameter tolerances.", className='error-message')

        # Build result output
        return html.Div([
            html.P(f"{len(matching_systems)} systems match.", className='success-message'),
        ])
    except Exception as e:
        import traceback
        print("Exception in estimate_two_parameters_callback:", e)
        print(traceback.format_exc())
        return html.P("Internal error during system matching.", className='error-message')


##############################    Run App   #############################
if __name__ == '__main__':
    data_folder_path = os.path.join(os.path.abspath(os.getcwd()), "systems_database")
    systems_db = db_calls.inspect_db(data_folder_path)
    app.run(debug=True)
