from dash import dcc, html

home_page = html.Div([

    html.Div([
        html.H2("Welcome to Binary Systems Analysis", className='section-title'),
        html.P("Analyze numerical simulations of binary systems.", className='section-description'),
        html.P("Each binary system is composed of a white dwarf and a companion object.", className='section-description'),
    ], className='section-container'),

], className='page-content')