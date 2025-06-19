from dash import Dash
import dash_bootstrap_components as dbc
from layout import Layout
from callbacks import register_callbacks

# Initialize the Dash app with a Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX], title="JalTantra Visualization", suppress_callback_exceptions=True)

# Set the layout of the app
app.layout = Layout().create_layout()

# Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
