import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
from dash.dependencies import Input
from dash.dependencies import Output

from utils import get_data_from_xml

app = dash.Dash(__name__)
name, df = get_data_from_xml()

app.layout = html.Div([
    html.Div([html.Div(name, style={'textAlign': 'center'}, className='dash-title'),
              html.Div([
                  html.Button('Табличный вид', id='btn-change-table', n_clicks=0, className='btn'),
                  html.Button('Графический вид', id='btn-change-graph', n_clicks=0, className='btn',
                              style={'marginTop': '5px'})
              ], className='buttons-box')], className='dash-header'),

    html.Div([
        html.Div(dash_table.DataTable(
            id='consuming-table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            style_cell={
                'whiteSpace': 'normal',
                'height': 'auto',
                'border': '1px solid #9c9c9c',
                'backgroundColor': '#323844'
            },
            style_header={'textAlign': 'center', 'backgroundColor': '#2a303a', 'font-weight': 'bold'},
            style_data={'textAlign': 'center'},
            style_table={'marginTop': '5px', 'color': '#acbcd5'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'},
                 'backgroundColor': '#353c48'},
                {
                    'if': {'state': 'selected'},
                    'backgroundColor': '#555a62',
                    'border': '1px solid white'
                }
            ]
        ), id='consuming-table-container'),
        html.Div([
            dcc.Graph(id='consuming-graph'),
            dcc.Dropdown(
                id='dropdown-graph',
                options=[{'label': f'Период {i}', 'value': i} for i in df.columns[2:]],
                value=1,
                searchable=False,
                placeholder='Выберите период...',
            ),
        ], id='consuming-graph-container')
    ], className='dash-container'),
], className='consuming-dashboard', style={'overflowX': 'auto'},
)


@app.callback(
    dash.dependencies.Output('consuming-table-container', 'style'),
    dash.dependencies.Output('consuming-graph-container', 'style'),
    Input('btn-change-table', 'n_clicks'),
    Input('btn-change-graph', 'n_clicks')
)
def display_btn(btn1, btn2):
    """change visibility between table and graph"""
    triggered_prop = [prop['prop_id'] for prop in dash.callback_context.triggered][0]
    prepared_styles = list()
    for btn_class in ('btn-change-table', 'btn-change-graph'):
        if btn_class in triggered_prop or btn_class == 'btn-change-graph' and triggered_prop == '.':
            prepared_styles.append({'display': 'flex'})
        else:
            prepared_styles.append({'display': 'none'})
    return prepared_styles


@app.callback(
    Output('consuming-graph', 'figure'),
    Input('btn-change-graph', 'n_clicks'),
    Input('dropdown-graph', 'value')
)
def data_to_graph(btn_click, select_period):
    """Convert data frame to graph"""
    prepared_df = df.groupby(['Точка учета'], as_index=True).sum().T
    select_period = int(select_period) - 1 if select_period else 0
    selected_data = prepared_df.iloc[select_period:]

    fig = px.line(selected_data, x=selected_data.index, y=selected_data.columns, template='plotly_dark')
    fig.update_layout(xaxis_title='Период', yaxis_title='Значение потребления кВт', hovermode="x",
                      title={'text': 'График потребления энергии', 'x': 0.5})
    fig.update_traces(mode='lines+markers', hovertemplate="Потребление: %{y}<extra><b>%{x}</b></extra>")
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
