import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import os
import base64
import plotly.graph_objs as go
import ast  # For safely evaluating the list input

from pages.home_page import home_page
from pages.db_page import db_page
from pages.data_analysis_page import data_analysis_page
from pages.data_visualization_page import data_visualization_page
from pages.advanced_search_page import advanced_search_page
from style import style

from callbacks import db_calls, estimators_calls
from files_utils import system_functions, demarcators, read_l, read_mat, estimators


# Global variables
systems_db = {}
data_folder_path = ""


# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Binary Systems"


# Add CSS
app.index_string = style


# Define the layout of the navigation bar
navbar_layout = html.Div([
    dcc.Link('Homepage', href='/', className='nav-link'),
    dcc.Link('Database', href='/db', className='nav-link'),
    dcc.Link('Data analysis', href='/analysis', className='nav-link'),
    #dcc.Link('Data visualization', href='/visualise', className='nav-link'),
    dcc.Link('Advanced search', href='/advanced', className='nav-link'),
], className='navbar')


# Define the main layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1("Analyzing Data of Binary Systems", className='main-header'),
    navbar_layout,
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    """Dynamically displays content based on the URL path."""
    if pathname == '/db': return db_page
    elif pathname == '/analysis': return data_analysis_page
    elif pathname == '/visualise': return data_visualization_page
    elif pathname == '/advanced': return advanced_search_page
    else: return home_page


@app.callback(Output('systems-list-output', 'children'), Input('load-systems-button', 'n_clicks'))
def load_database(n_clicks):
    """Loads and displays all systems from the database."""
    if not n_clicks:
        return "The binary systems that are in the database will appear here"
    
    try:
        if not systems_db:
            return html.P("No systems found in the database.", className='info-message')
        system_elements = []
        for sys_name, sys_files in sorted(systems_db.items()):
            l_files, mat_files = sys_files[0], sys_files[1]
            # Create a system card for each system
            system_card = html.Div([
                html.H4(f"System: {sys_name}"),
                
                # Display 'l' files
                html.Div([
                    html.H5("L Files:"),
                    html.Ul([html.Li(file) for file in l_files])
                ], className="l-files-section"),

                # Display 'mat' files
                html.Div([
                    html.H5("MAT Files:"),
                    html.Ul([html.Li(file) for file in mat_files])
                ], className="mat-files-section"),
                
            ], className='system-card')
            system_elements.append(system_card)
        return html.Div(system_elements)
    
    except Exception as e:
        return html.P(f"Error loading systems: {str(e)}", className='error-message')


@app.callback(
    Output("output-status", "children"),
    Input("upload-button", "n_clicks"),
    State("upload-csv", "contents"),
    State("upload-csv", "filename"),
    State("system_name", "value"),
)
def upload_new_system(n_clicks, contents, filenames, system_name):
    if not n_clicks:
        return ""
    if not system_name:
        return html.Div("⚠️ Please enter a system name.")
    if system_name in systems_db:
        return html.Div("⚠️ System alreay in the database.")
    if not contents:
        return html.Div("⚠️ No files uploaded.")

    if isinstance(contents, str):
        contents = [contents]
    if isinstance(filenames, str):
        filenames = [filenames]

    decoded_files = []
    for content, filename in zip(contents, filenames):
        _, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        decoded_files.append({"filename": filename, "content": decoded})

    try:
        db_calls.add_system(data_folder_path, system_name, decoded_files)
    except Exception as e:
        return html.Div(f"❌ Error in add_system: {e}")

    return html.Div(f"✅ {len(decoded_files)} file(s) added to system '{system_name}'.")


@app.callback(
    Output("update-upload-status-output", "children"),
    Input("submit-update-button", "n_clicks"),
    State("update-upload-data", "contents"),
    State("update-upload-data", "filename"),
    State("update-system-id", "value"),
    prevent_initial_call=True
)
def update_system_files(n_clicks, contents, filenames, system_name):
    if not contents:
        return html.Div("⚠️ No files selected.")
    if not system_name:
        return html.Div("⚠️ Please enter a system name.")
    if system_name not in systems_db:
        return html.Div(f"⚠️ System '{system_name}' not found.")

    messages = []
    for content, filename in zip(contents, filenames):
        try:
            _, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
        except Exception as e:
            messages.append(f"❌ {filename}: Failed to decode ({e})")
            continue

        try:
            db_calls.add_file_to_system(data_folder_path, system_name, filename, decoded)
            messages.append(f"✅ {filename} saved to {system_name}.")
        except Exception as e:
            messages.append(f"❌ {filename}: Error saving ({e})")

    return html.Ul([html.Li(msg) for msg in messages])


@app.callback(
    Output('temp-time-plot', 'figure'),
    Input('generate-temp-time-plot-button', 'n_clicks'),
    State('system-name-input-temp-time', 'value'),
    State('cycles-list-input-temp-time', 'value')
)
def plot_effective_temperature_vs_time(n_clicks, system_name, cycles_list_str):
    if n_clicks == 0 or not system_name or not cycles_list_str:
        # Return an empty figure initially
        return go.Figure()

    try:
        # convert the cycles list from an input string to a list
        cycles_list = ast.literal_eval(cycles_list_str)
        if not isinstance(cycles_list, list):
            raise ValueError
    except Exception:
        return go.Figure(layout=go.Layout(title="Invalid cycles list format. Use [10, 100, 200]"))

    # Call plot function
    files_lst = systems_db[system_name][0]
    system_path = os.path.join(data_folder_path, system_name)
    files_lst = [os.path.join(system_path, f) for f in files_lst]
    system = read_l.concatenate_files(files_lst)
    fig = system_functions.draw_cycles(system , cycles_list, demarcators.demarcate_decay_phases)
    return fig


@app.callback(Output('cycle-length-t3-plot', 'figure'), Input('generate-cycle-t3-plot-button', 'n_clicks'), State('system-name-input-cycle-t3', 'value'))
def plot_cycle_length_t3_plot(n_clicks, system_name):
    """Generates a cycle length vs T3 plot for the selected system."""
    if n_clicks > 0 and system_name:
        if system_name not in systems_db: return {'data': [], 'layout': go.Layout(title=f'System "{system_name}" not found.', xaxis={'visible': False}, yaxis={'visible': False})}
        files_lst_l = systems_db[system_name][0]
        files_lst_mat = systems_db[system_name][1]
        system_path = os.path.join(data_folder_path, system_name)
        files_lst_l = [os.path.join(system_path, f) for f in files_lst_l]
        files_lst_mat = [os.path.join(system_path, f) for f in files_lst_mat]
        l_df = read_l.concatenate_files(files_lst_l)
        mat_df = read_mat.concatenate_files(files_lst_mat)
        return system_functions.draw_cycles_lengths_vs_t3(l_df, mat_df)
    return {}



@app.callback(
    Output('last-nova-output', 'children'),
    Input('estimate-nova-button', 'n_clicks'),
    State('wd-mass-input', 'value'), State('wd-mass-delta-input', 'value'),
    State('comp-mass-input', 'value'), State('comp-mass-delta-input', 'value'),
    State('eff-temp-input', 'value'), State('eff-temp-delta-input', 'value'),
    prevent_initial_call=True
)
def estimate_last_nova_callback(n_clicks,
                                 wd_mass, wd_mass_delta,
                                 comp_mass, comp_mass_delta,
                                 eff_temp, eff_temp_delta):
    """Estimate last nova time by matching inputs to dataset."""

    # Ensure all inputs are present
    if any(v is None for v in [wd_mass, wd_mass_delta,
                               comp_mass, comp_mass_delta,
                               eff_temp, eff_temp_delta]):
        return html.P("Please fill in all input fields (including deltas).", className='error-message')

    # Make margin dict from user inputs
    margins = {
        'MWD': [wd_mass, wd_mass_delta],
        'MRD': [comp_mass, comp_mass_delta],
        'effective temperature': [eff_temp, eff_temp_delta],
    }

    dfs = estimators_calls.retreive_systems_with_companion_mass(systems_db, "wd_comp_mass", data_folder_path)
    time = estimators.estimate_nova(dfs, margins)

    if time == -1:
        return html.P("No match found.", className='error-message')

    return html.Div([
        html.P(f"Last nova estimated {time:.3f} years ago", className='success-message')
    ])



@app.callback(
    Output('fourth-param-output', 'children'),
    Input('predict-fourth-param-button', 'n_clicks'),
    State('param1-dropdown', 'value'), State('param1-value', 'value'), State('param1-delta', 'value'),
    State('param2-dropdown', 'value'), State('param2-value', 'value'), State('param2-delta', 'value'),
    State('param3-dropdown', 'value'), State('param3-value', 'value'), State('param3-delta', 'value'),
    prevent_initial_call=True
)
def predict_fourth_parameter_callback(n_clicks, 
                                      p1n, p1v, p1d,
                                      p2n, p2v, p2d,
                                      p3n, p3v, p3d):
    # Ensure three selections with values/deltas
    inputs = [(p1n, p1v, p1d), (p2n, p2v, p2d), (p3n, p3v, p3d)]
    if any(name is None or val is None or delta is None for name, val, delta in inputs):
        return html.P("Please select three parameters and enter all values & deltas.", className='error-message')

    # Check uniqueness of parameter names
    names = {p1n, p2n, p3n}
    if len(names) != 3:
        return html.P("Please select three *unique* parameters.", className='error-message')

    # Build margins dict
    margins = {
        name: [val, delta] for name, val, delta in inputs
    }

    # Determine the missing 4th parameter
    all_params = {"MWD", "MRD", "time", "effective temperature"}
    missing = (all_params - names)
    print(missing)
    if len(missing) != 1:
        return html.P("Internal error: could not identify missing parameter.", className='error-message')
    missing_param = missing.pop()

    # Call estimation logic
    dfs = estimators_calls.retreive_systems_with_companion_mass(systems_db, "wd_comp_mass", data_folder_path)
    estimate = estimators.find_closest_system(dfs, margins)
    if estimate[2].empty:
        return html.P("No system found within the given tolerances.", className='error-message')

    closest_row = estimate[2]
    if not closest_row.empty:
        # find time and cycle number at the closest row:
        predicted_value = closest_row[missing]
        if missing_param == "time":
            time = closest_row["time"]
            cycle = closest_row["cycle"]
            cycles_timing = demarcators.demarcate_nova_eruptions(estimate[0])
            predicted_value = time - cycles_timing[cycle][0]

    return html.P(f"Estimated {missing_param}: {predicted_value:.3f}", className='success-message')








if __name__ == '__main__':
    data_folder_path = os.path.join(os.path.abspath(os.getcwd()), "mat_l_data")
    systems_db = db_calls.inspect_db(data_folder_path)
    app.run(debug=True)
