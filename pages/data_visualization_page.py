from dash import dcc, html


data_visualization_page = html.Div([
    html.H2("Data Analysis", className='page-title'),
    html.P("This page will host tools and visualizations for in-depth data analysis of binary systems. "
           "Please enter the system name for each plot."),
    html.Div([
        html.H3("Effective temperature vs time", className='section-title'), # Changed title to be more general for draw_cycles
        html.P("Enter system name and optionally a list of cycles to generate a cycles plot."),
        dcc.Input(id='system-name-input-temp-time', type='text', placeholder='Enter System Name', className='text-input'),
        dcc.Input(id='cycles-list-input-temp-time', type='text', placeholder='Enter cycles list (e.g., [1.2, 1.5, 1.1]) or leave blank to use system data', className='text-input'),
        html.Button("Generate Cycles Plot", id="generate-temp-time-plot-button", n_clicks=0, className='button primary-button'),
        dcc.Graph(id='temp-time-plot', className='plot-area') # Renamed from temp-time-plot as it's now a cycles plot
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
