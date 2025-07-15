from dash import dcc, html

explore_system_page = html.Div([

    # SECTION 1: Select System
    html.Div([
        html.H3("Select System to Explore", className='section-title'),
        html.P("Choose a system to load and explore its data files and info.", className='section-description'),
        html.Div([
            html.Label("System Name:", className='input-label'),
            dcc.Dropdown(id='system-name-dropdown',placeholder='Select system...',className='dropdown-input',),
        ], className='input-group'),
        html.Button("Load System", id='load-button', n_clicks=0, className='button'),

        html.Div(id='files-list-to_display', className='output-area'),
        html.Div(id='system-info-output', className='output-area'),
    ], className='section-container'),

    html.Hr(className='section-divider'),

    # SECTION 2: Display Table
    html.Div([
        html.H3("Display Table", className='section-title'),
        html.P("Select the file type and customize which columns and rows to display."),
        
        html.Div([
            html.Div([
                html.Label("Select File Type:", className='input-label'),
                dcc.Dropdown(
                    id='df-selector-display-table', 
                    placeholder='Select file type...', 
                    className='dropdown-input',
                    options=[{'label': 'L files', 'value': 'L'},{'label': 'MAT files', 'value': 'MAT'},{'label': 'Merged files', 'value': 'Merged'}
            ]),
            ], className='input-group'),

            html.Div([
                html.Label("Choose Columns:", className='input-label'),
                dcc.Dropdown(id='df-column-selector', multi=True, placeholder='Choose columns...', className='dropdown-input', options=[]),
            ], className='input-group'),

            html.Div([
                html.Div([
                    html.Label("Start Row:", className='input-label'),
                    dcc.Input(id='row-start', type='number', min=0, placeholder='Start Row', className='text-input numeric-input')
                ], className='input-group half-width margin-right'),

                html.Div([
                    html.Label("End Row:", className='input-label'),
                    dcc.Input(id='row-end', type='number', min=1, placeholder='End Row', className='text-input numeric-input'),
                ], className='input-group half-width'),
            ], className='input-pair-container'),
        ], className='form-container'),

        html.Button("Show Table", id='show-df-button', n_clicks=0, className='button'),
        html.Div(id='df-output', className='output-area'),
    ], className='section-container'),

    html.Hr(className='section-divider'),

    # SECTION 3: Plot Two Parameters
    html.Div([
        html.H3("Plot Two Parameters", className='section-title'),
        html.P("Select two parameters to plot against each other. You can apply log scaling to either one."),

        html.Div([
                html.Label("Select File Type:", className='input-label'),
                dcc.Dropdown(
                    id='df-selector-plot', 
                    placeholder='Select file type...', 
                    className='dropdown-input',
                    options=[{'label': 'L files', 'value': 'L'},{'label': 'MAT files', 'value': 'MAT'},{'label': 'Merged files', 'value': 'Merged'}
            ]),
        ], className='input-group'),

        html.Div([
            html.Div([
                html.Label("First Column:", className='input-label'),
                dcc.Dropdown(
                    id='plot-col1',
                    options=[],
                    placeholder='Select first column...',
                    className='dropdown-input',
                ),
                html.Div([
                    dcc.Checklist(
                        id='log-scale-col1',
                        options=[{'label': 'Apply log scale', 'value': 'log'}],
                        value=[],
                        className='checkbox-group'
                    )
                ])
            ], className='input-group half-width margin-right'),

            html.Div([
                html.Label("Second Column:", className='input-label'),
                dcc.Dropdown(
                    id='plot-col2',
                    options=[],
                    placeholder='Select second column...',
                    className='dropdown-input',
                ),
                html.Div([
                    dcc.Checklist(
                        id='log-scale-col2',
                        options=[{'label': 'Apply log scale', 'value': 'log'}],
                        value=[],
                        className='checkbox-group'
                    )
                ])
            ], className='input-group half-width'),
        ], className='input-pair-container'),

        html.Button("Plot", id='plot-button', n_clicks=0, className='button'),
        html.Div(id='plot-output', className='output-area'),
    ], className='section-container'),

    html.Hr(className='section-divider'),

    # SECTION 4: Plot Cycle Length
    html.Div([
        html.H3("Plot Cycle Length vs Column", className='section-title'),
        html.P("Select a column to plot against cycle length."),

        html.Div([
            html.Label("Select Column:", className='input-label'),
            dcc.Dropdown(
                id='cycle-length-col-dropdown',
                options=[],
                placeholder='Select column...',
                className='dropdown-input',
            ),
        ], className='input-group half-width'),

        html.Div([
            dcc.Checklist(
                id='log-scale-checklist',
                options=[
                    {'label': 'Apply log on selected column', 'value': 'log_x'},
                    {'label': 'Apply log on cycle length', 'value': 'log_y'},
                ],
                value=[]
            )
        ], className='input-group half-width'),

        html.Button("Plot", id='plot-cycle-length-button', n_clicks=0, className='button'),
        html.Div(id='plot-cycle-length-output', className='output-area'),
    ], className='section-container')


], className='page-content')
