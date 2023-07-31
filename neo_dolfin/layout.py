import dash_core_components as dcc
import dash_html_components as html

layout = html.Div([
    html.H1('Dash Application'),
    dcc.Graph(id='example-graph', figure={'data': [{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'}]}),
])