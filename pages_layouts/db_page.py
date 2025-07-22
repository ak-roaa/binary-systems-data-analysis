from dash import dcc, html

db_page = html.Div([

    # SECTION 1: View Systems
    html.Div([
        html.H3("View Systems", className='section-title'),
        html.P("Browse and inspect the binary systems currently in the database."),
        html.Button("View All Systems", id="load-systems-button", n_clicks=0, className='button'),
        html.Div(id="systems-list-output", className='output-area'),
    ], className='section-container'),

    html.Hr(className='section-divider'),

    # SECTION 2: Upload a New System
    html.Div([
        html.H3("Upload a New System", className='section-title'),
        html.P("Upload a collection of files to create a new binary system entry."),

        html.Div([
            html.Label("System Name:", className='input-label'),
            dcc.Input(id='system-name-input', type='text', placeholder='Enter new system name', className='text-input'),
        ], className='input-group'),

        html.Div([
            html.Label("System Files:", className='input-label'),
            dcc.Upload(
                id='input-files',
                children=html.Div(['Drop or ', html.A('Select Files')]),
                multiple=True,
                className='upload-area'
            ),
        ], className='input-group'),

        html.Button("Upload Files", id='system-upload-button', n_clicks=0, className='button'),
        html.Div(id='system-upload-output', className='output-area'),
    ], className='section-container'),

    html.Hr(className='section-divider'),

    # SECTION 3: Update an Existing System's Files
    html.Div([
        html.H3("Update an Existing System's Files", className='section-title'),
        html.P("You can add or delete files, or remove the entire system from the database."),

        html.Div([
            html.Label("System Name:", className='input-label'),
            dcc.Input(id='existing-system-id', type='text', placeholder='Enter existing system name', className='text-input'),
        ], className='input-group'),

        html.Div([
            html.Label("File Name to Add/Delete:", className='input-label'),
            dcc.Input(id='file-name', type='text', placeholder='Enter filename', className='text-input'),
        ], className='input-group'),

        html.Div([
            html.Label("Upload Files:", className='input-label'),
            dcc.Upload(
                id='uploaded-file',
                children=html.Div(['Drop or ', html.A('Select Files to Update')]),
                multiple=True,
                className='upload-area'
            ),
        ], className='input-group'),

        html.Div([
            html.Button("Add File", id="add-file-button", n_clicks=0, className='button button-margin-right'),
            html.Button("Delete File", id="delete-file-button", n_clicks=0, className='button button-margin-right'),
            html.Button("Delete System", id="delete-system-button", n_clicks=0, className='button'),
        ], className='button-group button-margin-top'),

        html.Div(id='update-existing-system-output', className='output-area'),
    ], className='section-container'),

    html.Hr(className='section-divider'),

], className='page-content')
