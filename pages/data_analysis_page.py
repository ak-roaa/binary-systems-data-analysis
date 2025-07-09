from dash import dcc, html


data_analysis_page = html.Div([
    html.H2("Data Analysis", className='page-title'),
    html.Div([
        html.H3("Effective temperature vs time", className='section-title'),
        html.P("Enter system name and the cycles for which to generate plots of effective temperature decay after a nova eruption."),
        dcc.Input(id='system-name-input-temp-time', type='text', placeholder='Enter System Name', className='text-input'),
        dcc.Input(id='cycles-list-input-temp-time', type='text', placeholder='Enter cycles list (e.g., [10, 100, 200])', className='text-input'),
        html.Button("Plot", id="generate-temp-time-plot-button", n_clicks=0, className='button primary-button'),
        dcc.Graph(id='temp-time-plot', className='plot-area')
    ], className='section-container plot-section'),
    html.Hr(className='section-divider'),
    html.Div([
        html.H3("Cycle Length vs. T3", className='section-title'),
        html.P("Enter system name to visualize cycle length against T3."),
        dcc.Input(id='system-name-input-cycle-t3', type='text', placeholder='Enter System Name', className='text-input'),
        html.Button("Generate Cycle vs T3 Plot", id="generate-cycle-t3-plot-button", n_clicks=0, className='button primary-button'),
        dcc.Graph(id='cycle-length-t3-plot', className='plot-area')
    ], className='section-container plot-section'),
    html.Hr(className='section-divider'),
    html.Div([
        html.H3("Cycle Length vs. Tmax", className='section-title'),
        html.P("Enter system name to visualize cycle length against maximum temperature."),
        dcc.Input(id='system-name-input-cycle-tmax', type='text', placeholder='Enter System Name', className='text-input'),
        html.Button("Generate Cycle vs Tmax Plot", id="generate-cycle-tmax-plot-button", n_clicks=0, className='button primary-button'),
        dcc.Graph(id='cycle-length-tmax-plot', className='plot-area')
    ], className='section-container plot-section'),
], className='page-content data-analysis-page')
