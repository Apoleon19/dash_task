import dash
import dash_html_components as html
from utils import get_xml_data_file
from collections import defaultdict

import dash
import dash_table
import pandas as pd

app = dash.Dash(__name__)
name, df = get_xml_data_file()

# app.layout = html.Div(className="container", children=[
#     html.H1(className="container__title", children=name),
#     html.Div(children="test"),
#
#
# ])

#

app.layout = dash_table.DataTable(
    id='table',
    # columns=[gen_table_period_columns()],
    # data=gen_table_period_columns(),
)


if __name__ == '__main__':
    # gen_table_period_columns()
    app.run_server(debug=True)