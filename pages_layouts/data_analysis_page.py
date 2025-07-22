from dash import dcc, html

data_analysis_page = html.Div([

    html.Div([
        html.H3("Plot decay of effective temperature after eruption", className='section-title'),
        html.P("Enter the system name and select cycles to plot their effective temperature over time.", className='section-description'),

        html.Div([
            html.Label("System Name:", className='input-label'),
            dcc.Dropdown(
                id='system-name-dropdown-temp-time',
                placeholder='Select system name',
                className='dropdown-input',
                options=[]  # Will be filled dynamically via callback
            ),
        ], className='input-group'),

        html.Div([
            html.Label("Cycles List (e.g., [10, 100, 200]):", className='input-label'),
            dcc.Input(
                id='cycles-list-input-temp-time',
                type='text',
                placeholder='Enter cycles list',
                className='text-input',
            ),
        ], className='input-group'),

        html.Button("Generate Plot", id='generate-temp-time-plot-button', n_clicks=0, className='button'),

        html.Div(id='temp-time-plot', className='output-area'),

    ], className='section-container')

], className='page-content uniform-page')
