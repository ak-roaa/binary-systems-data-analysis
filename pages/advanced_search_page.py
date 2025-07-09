from dash import dcc, html

parameter_options = [
    {'label': 'White Dwarf Mass (M☉)', 'value': 'MWD'},
    {'label': 'Companion Mass (M☉)', 'value': 'MRD'},
    {'label': 'Time (Years)', 'value': 'time'},
    {'label': 'Effective Temperature (log K)', 'value': 'effective temperature'}
]

advanced_search_page = html.Div([
    html.H2("Advanced Search", className='page-title'),

    # Section 1: Estimate timing of the last nova
    html.Div([
        html.H3("Estimate timing of the last nova", className='section-title'),
        html.P("Estimate the timing of the last nova based on the system's effective temperature."),
        
        html.Div([
            html.Div([
                html.Label("White Dwarf Mass (M☉):", className='input-label'),
                dcc.Input(id='wd-mass-input', type='number', placeholder='e.g., 0.6', min=0.1, max=1.4, step=0.01, className='text-input numeric-input'),
            ], className='input-group'),
            html.Div([
                html.Label("Tolerance interval:", className='input-label'),
                dcc.Input(id='wd-mass-delta-input', type='number', placeholder='e.g., 0.0005', min=0, step=0.01, className='text-input numeric-input delta-input'),
            ], className='input-group'),
        ], className='input-pair-container'),

        html.Div([
            html.Div([
                html.Label("Companion Mass (M☉):", className='input-label'),
                dcc.Input(id='comp-mass-input', type='number', placeholder='e.g., 0.0003', min=0.01, max=1.0, step=0.01, className='text-input numeric-input'),
            ], className='input-group'),
            html.Div([
                html.Label("Tolerance interval:", className='input-label'),
                dcc.Input(id='comp-mass-delta-input', type='number', placeholder='e.g., 0.0002', min=0, step=0.01, className='text-input numeric-input delta-input'),
            ], className='input-group'),
        ], className='input-pair-container'),

        html.Div([
            html.Div([
                html.Label("Effective Temperature (log K):", className='input-label'),
                dcc.Input(id='eff-temp-input', type='number', placeholder='e.g., 4.2', min=3.0, max=5.0, step=0.01, className='text-input numeric-input'),
            ], className='input-group'),
            html.Div([
                html.Label("Tolerance interval:", className='input-label'),
                dcc.Input(id='eff-temp-delta-input', type='number', placeholder='e.g., 0.01', min=0, step=0.01, className='text-input numeric-input delta-input'),
            ], className='input-group'),
        ], className='input-pair-container'),

        html.Button("Estimate", id="estimate-nova-button", n_clicks=0, className='button primary-button'),
        html.Div(id='last-nova-output', className='output-area'),

    ], className='section-container advanced-search-section'),

    html.Hr(className='section-divider'),

    # Section 2: Estimate Fourth Parameter
    html.Div([
        html.H3("Estimate Fourth Parameter", className='section-title'),
        
        # Parameter 1 Selection and Inputs
        html.Div([
            html.Div([
                html.Label("Parameter 1:", className='input-label'),
                dcc.Dropdown(
                    id='param1-dropdown',
                    options=parameter_options,
                    placeholder="Select Parameter 1",
                    className='dropdown-input'
                ),
            ], className='input-group'),
            html.Div([
                html.Label("Value 1:", className='input-label'),
                dcc.Input(id='param1-value', type='number', placeholder='Value', className='text-input numeric-input'),
            ], className='input-group'),
            html.Div([
                html.Label("Tolerance interval:", className='input-label'),
                dcc.Input(id='param1-delta', type='number', placeholder='Delta', min=0, step=0.01, className='text-input numeric-input delta-input'),
            ], className='input-group'),
        ], className='input-triple-container'),

        # Parameter 2 Selection and Inputs
        html.Div([
            html.Div([
                html.Label("Parameter 2:", className='input-label'),
                dcc.Dropdown(
                    id='param2-dropdown',
                    options=parameter_options,
                    placeholder="Select Parameter 2",
                    className='dropdown-input'
                ),
            ], className='input-group'),
            html.Div([
                html.Label("Value 2:", className='input-label'),
                dcc.Input(id='param2-value', type='number', placeholder='Value', className='text-input numeric-input'),
            ], className='input-group'),
            html.Div([
                html.Label("Tolerance interval:", className='input-label'),
                dcc.Input(id='param2-delta', type='number', placeholder='Delta', min=0, step=0.01, className='text-input numeric-input delta-input'),
            ], className='input-group'),
        ], className='input-triple-container'),

        # Parameter 3 Selection and Inputs
        html.Div([
            html.Div([
                html.Label("Parameter 3:", className='input-label'),
                dcc.Dropdown(
                    id='param3-dropdown',
                    options=parameter_options,
                    placeholder="Select Parameter 3",
                    className='dropdown-input'
                ),
            ], className='input-group'),
            html.Div([
                html.Label("Value 3:", className='input-label'),
                dcc.Input(id='param3-value', type='number', placeholder='Value', className='text-input numeric-input'),
            ], className='input-group'),
            html.Div([
                html.Label("Tolerance interval:", className='input-label'),
                dcc.Input(id='param3-delta', type='number', placeholder='Delta', min=0, step=0.01, className='text-input numeric-input delta-input'),
            ], className='input-group'),
        ], className='input-triple-container'),

        html.Button("Estimate", id="predict-fourth-param-button", n_clicks=0, className='button primary-button'),
        html.Div(id='fourth-param-output', className='output-area'),

    ], className='section-container advanced-search-section'),

    html.Hr(className='section-divider'),

    # Section 3: Estimate Two Parameters
    html.Div([
        html.H3("Estimate Two Parameters", className='section-title'),
        html.P("Select two parameters and provide their values and tolerance. Systems that include phases with values will be searched ."),
        
        # Parameter 1 Selection and Inputs
        html.Div([
            html.Div([
                html.Label("Parameter 1:", className='input-label'),
                dcc.Dropdown(
                    id='param1-two-dropdown',
                    options=parameter_options,
                    placeholder="Select Parameter 1",
                    className='dropdown-input'
                ),
            ], className='input-group'),
            html.Div([
                html.Label("Value 1:", className='input-label'),
                dcc.Input(id='param1-two-value', type='number', placeholder='Value', className='text-input numeric-input'),
            ], className='input-group'),
            html.Div([
                html.Label("Tolerance interval:", className='input-label'),
                dcc.Input(id='param1-two-delta', type='number', placeholder='Delta', min=0, step=0.01, className='text-input numeric-input delta-input'),
            ], className='input-group'),
        ], className='input-triple-container'),

        # Parameter 2 Selection and Inputs
        html.Div([
            html.Div([
                html.Label("Parameter 2:", className='input-label'),
                dcc.Dropdown(
                    id='param2-two-dropdown',
                    options=parameter_options,
                    placeholder="Select Parameter 2",
                    className='dropdown-input'
                ),
            ], className='input-group'),
            html.Div([
                html.Label("Value 2:", className='input-label'),
                dcc.Input(id='param2-two-value', type='number', placeholder='Value', className='text-input numeric-input'),
            ], className='input-group'),
            html.Div([
                html.Label("Tolerance interval:", className='input-label'),
                dcc.Input(id='param2-two-delta', type='number', placeholder='Delta', min=0, step=0.01, className='text-input numeric-input delta-input'),
            ], className='input-group'),
        ], className='input-triple-container'),

        html.Button("Estimate", id="estimate-two-params-button", n_clicks=0, className='button primary-button'),
        html.Div(id='estimated-two-params-output', className='output-area'),

    ], className='section-container advanced-search-section'),

], className='page-content advanced-search-page')

