from dash import dcc, html

db_page = html.Div([
    html.Div([
        html.H3("View Systems", className='section-title'),
        html.P("Browse and inspect the binary systems currently in the database."),
        html.Button("Load All Systems", id="load-systems-button", n_clicks=0, className='button primary-button'),
        html.Div(id="systems-list-output", className='output-area'),
    ], className='section-container view-systems-section'),
    
    html.Hr(className='section-divider'),
    
    html.Div([
        html.H3("Upload a New System", className='section-title'),
        html.P("Upload a collection of files to create a new binary system entry."),
        dcc.Input(id='system_name', type='text', placeholder='Enter new system name', className='text-input'),
        
        dcc.Upload(
            id='upload-csv',
            children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '2px', 'borderStyle': 'dashed', 'borderRadius': '10px',
                'textAlign': 'center', 'margin': '20px 0', 'cursor': 'pointer',
                'backgroundColor': '#f9fafb', 'borderColor': '#d1d5db', 'color': '#4b5563'
            },
            multiple=True,
            className='upload-area'
        ),
        
        html.Button("Upload Files", id='upload-button', n_clicks=0, className='button success-button'),
        
        html.Div(id='output-status', className='output-area'),
    ], className='section-container upload-system-section'),
    
    html.Hr(className='section-divider'),
    
    html.Div([
        html.H3("Update an Existing System", className='section-title'),
        dcc.Input(id='update-system-id', type='text', placeholder='Enter System name', className='text-input'),
        dcc.Upload(
            id='update-upload-data',
            children=html.Div(['Drag and Drop or ', html.A('Select Files to Update')]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '2px', 'borderStyle': 'dashed', 'borderRadius': '10px',
                'textAlign': 'center', 'margin': '20px 0', 'cursor': 'pointer',
                'backgroundColor': '#f9fafb', 'borderColor': '#d1d5db', 'color': '#4b5563'
            },
            multiple=True,
            className='upload-area'
        ),
        
        html.Div(id='update-upload-status-output', className='output-area'),
        html.Button("Update", id="submit-update-button", n_clicks=0, className='button warning-button'),
        html.Div(id='update-system-output', className='output-area'),
    ], className='section-container update-system-section'),
], className='page-content database-page')
