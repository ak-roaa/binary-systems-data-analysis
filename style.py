
# Add some CSS for styling
style = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f3f4f6;
                color: #333;
            }
            .main-header {
                font-size: 3.5em;
                font-weight: 900;
                color: #2c5282;
                text-align: center;
                padding: 30px 0;
                margin-top: 20px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.15);
            }
            .navbar {
                display: flex;
                justify-content: center;
                gap: 20px;
                background-color: #1a202c;
                padding: 15px 0;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .nav-link {
                color: #e2e8f0;
                text-decoration: none;
                padding: 10px 15px;
                border-radius: 8px;
                transition: background-color 0.3s ease, color 0.3s ease;
                font-weight: bold;
            }
            .nav-link:hover {
                background-color: #2d3748;
                color: #a0aec0;
            }
            .page-content {
                max-width: 900px;
                margin: 40px auto;
                padding: 30px;
                background-color: #ffffff;
                border-radius: 12px;
                box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            .page-title {
                color: #2c5282;
                margin-bottom: 30px;
                font-size: 2.8em;
                font-weight: 800;
            }
            p {
                line-height: 1.6;
                font-size: 1.1em;
                color: #4a5568;
                margin-bottom: 15px;
            }
            h2 {
                font-size: 1.8em;
                color: #2c5282;
            }

            .database-page {
                display: flex;
                flex-direction: column;
                gap: 30px;
            }
            .section-container {
                padding: 25px;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                background-color: #fcfcfc;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                text-align: left;
            }
            .section-title {
                color: #3182ce;
                font-size: 1.8em;
                margin-bottom: 15px;
                font-weight: 700;
                text-align: center;
            }
            .section-divider {
                border: 0;
                height: 1px;
                background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0));
                margin: 40px 0;
            }
            .button {
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
                transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.2s ease;
                margin-top: 15px;
                display: inline-block;
            }
            .button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            .primary-button {
                background-color: #4299e1;
                color: white;
            }
            .primary-button:hover {
                background-color: #3182ce;
            }
            .success-button {
                background-color: #48bb78;
                color: white;
            }
            .success-button:hover {
                background-color: #38a169;
            }
            .warning-button {
                background-color: #ed8936;
                color: white;
            }
            .warning-button:hover {
                background-color: #dd6b20;
            }

            .text-input {
                width: calc(100% - 22px);
                padding: 10px;
                margin-bottom: 15px;
                border: 1px solid #cbd5e0;
                border-radius: 8px;
                box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.06);
                font-size: 1em;
            }
            .text-input:focus {
                outline: none;
                border-color: #63b3ed;
                box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.5);
            }
            .numeric-input {
                width: 100%; /* Adjust as needed for input group */
            }
            .dropdown-input .Select-control { /* Dash dropdown styling */
                border: 1px solid #cbd5e0;
                border-radius: 8px;
                box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.06);
                font-size: 1em;
                min-height: 40px; /* Ensure consistent height with text inputs */
            }
            .dropdown-input .Select-control:hover {
                border-color: #63b3ed;
            }
            .dropdown-input .Select-value {
                padding-top: 8px; /* Adjust text vertical alignment */
            }
            .dropdown-input .Select-menu-outer {
                border-radius: 8px;
                border-color: #cbd5e0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .dropdown-input .Select-option.is-focused {
                background-color: #ebf8ff; /* Light blue background for focused option */
            }
            .dropdown-input .Select-option.is-selected {
                background-color: #3182ce; /* Blue background for selected option */
                color: white;
            }
            .dropdown-input .Select-placeholder {
                color: #a0aec0; /* Lighter placeholder text */
            }


            .output-area {
                margin-top: 20px;
                padding: 15px;
                background-color: #e0f2f7;
                border-left: 4px solid #3182ce;
                border-radius: 8px;
                color: #2b6cb0;
            }
            .system-card {
                background-color: #f0f4f8;
                border: 1px solid #d1d9e6;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
                text-align: left;
            }
            .system-card h4 {
                color: #2c5282;
                margin-top: 0;
                margin-bottom: 5px;
                font-size: 1.3em;
            }
            .system-card p {
                font-size: 0.95em;
                color: #4a5568;
                margin-bottom: 5px;
            }
            .info-message {
                color: #2c5282;
                background-color: #e0f2f7;
                padding: 8px;
                border-radius: 5px;
                border-left: 3px solid #3182ce;
                margin-top: 10px;
                font-size: 0.9em;
            }
            .success-message {
                color: #2f855a;
                background-color: #d4edda;
                padding: 8px;
                border-radius: 5px;
                border-left: 3px solid #38a169;
                margin-top: 10px;
                font-size: 0.9em;
            }
            .error-message {
                color: #c53030;
                background-color: #fed7d7;
                padding: 8px;
                border-radius: 5px;
                border-left: 3px solid #e53e3e;
                margin-top: 10px;
                font-size: 0.9em;
            }
            .warning-message {
                color: #975a16;
                background-color: #feebc8;
                padding: 8px;
                border-radius: 5px;
                border-left: 3px solid #dd6b20;
                margin-top: 10px;
            }
            .data-analysis-page .plot-section {
                padding: 20px;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                background-color: #fcfcfc;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                text-align: center;
                margin-bottom: 20px; /* Space between sections */
            }
            .data-analysis-page .plot-section .section-title {
                margin-top: 0;
                margin-bottom: 10px;
            }
            .plot-area {
                margin-top: 20px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                overflow: hidden; /* Ensures plot fits within border-radius */
            }
            /* Styles for Advanced Search Page */
            .advanced-search-page .section-container {
                text-align: left;
                margin-bottom: 30px;
            }
            .advanced-search-page .input-label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
                color: #2d3748;
                font-size: 0.95em;
            }
            .advanced-search-page .input-pair-container,
            .advanced-search-page .input-triple-container { /* New style for triple input groups */
                display: flex;
                gap: 20px;
                margin-bottom: 15px;
            }
            .advanced-search-page .input-group {
                flex: 1;
            }
            .advanced-search-page .numeric-input {
                width: 100%;
                box-sizing: border-box; /* Include padding and border in the element's total width and height */
            }
            .advanced-search-page .delta-input {
                background-color: #f8fafc;
                border-color: #e2e8f0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

