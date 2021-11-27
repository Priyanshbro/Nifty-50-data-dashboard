import dash_bootstrap_components as dbc
import dash
from dash import html
from dash import dcc
from dash.dependencies import Output, Input
from app import app
from data import all_stock_df

#-------------------------------------------------------------------------------------------------------------
# Connect to the layout of each tab
from stocks import stocks_layout
from sectors import sectors_layout

#-------------------------------------------------------------------------------------------------------------
# App layout
app_tabs = html.Div(
    [
        dbc.Row(
            [
                dbc.Tabs(
                    [
                        dbc.Tab(label="Stocks", tab_id="tab-stocks",
                                labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
                        dbc.Tab(label="Sectors", tab_id="tab-sectors",
                                labelClassName="text-success font-weight-bold", activeLabelClassName="text-danger"),
                    ],
                    id="tabs",
                    active_tab="tab-stocks",
                ),
                html.Div(
                    [
                        dbc.Button("Download CSV", color="primary",
                                   className="mr-1", id="btn_csv"),
                        dcc.Download(id="download-dataframe-csv"),
                    ], style={"marginLeft": "50rem"}
                )
            ])

    ], className="mt-3"
)

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Sectorwise Stock Trends",
                            style={"textAlign": "center", "padding": "1rem"}), width=12)),
    html.Hr(),
    dbc.Row(dbc.Col(app_tabs, width=12), className="mb-3"),
    html.Div(id='content', children=[])

])

#-------------------------------------------------------------------------------------------------------------
# Callbacks
@app.callback(
    Output("content", "children"),
    [Input("tabs", "active_tab")]
)
def switch_tab(tab_chosen):
    if tab_chosen == "tab-stocks":
        return stocks_layout
    elif tab_chosen == "tab-sectors":
        return sectors_layout
    return html.P("Please select a Tab")


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(all_stock_df.to_csv, "stock_data.csv")


if __name__ == '__main__':
# Running the server
    app.run_server(debug=True)
