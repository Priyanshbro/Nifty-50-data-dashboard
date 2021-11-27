import plotly.express as px
from datetime import date
from dash import html
from dash import dcc
import dash_daq as daq
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from data import all_stock_df, industries
from app import app

# -------------------------------------------------------------------------------------------------------------
# Sector tab Layout
sectors_layout = html.Div(
    [
        # -------------------------------------------------------------------------------------------------------------
        # Dropdown row
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Select Sectors"),
                        dcc.Dropdown(
                            id="dd-sector-multi",
                            multi=True,
                            value=list(industries.keys()),
                            options=[
                                {"label": stock, "value": stock}
                                for stock in all_stock_df["Industry"].unique()
                            ],
                            clearable=False,
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.Label("Select Date Range"),
                        dcc.DatePickerRange(
                            id='date-picker-range-sector',
                        )
                    ],
                    width=4,
                ),
                dbc.Row(
                    [
                        dbc.Col([
                            daq.BooleanSwitch(
                                id="switch-percent-sector",
                                label='Percent change',
                                labelPosition='bottom'
                            )], style={"paddingLeft": "2rem", "paddingTop": "1rem"}),
                        dbc.Button("Apply changes", color="info",
                                   className="mr-1", id="btn-sector-run", style={"margin": "2rem"}),
                    ]),
            ],
            className="mt-4",

        ),
        # -------------------------------------------------------------------------------------------------------------
        # Sector graph row
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id="graph-sector", figure={}),

                    ],
                    width=8),


                dbc.Col(
                    [
                        daq.Gauge(
                            style={"marginTop": "6rem"},
                            id='gauge-sector',
                            scale={"custom": {1: {"label": "Bearish"},
                                              3: {"label": "Bullish"}}},
                            label="Market Indicator",
                            value=0,
                            max=4,
                            min=0,
                            color={"gradient": True, "ranges": {
                                "red": [0, 1.33], "yellow":[1.33, 2.66], "green":[2.66, 4]}},
                        ),
                    ],
                    width=4),
            ]
        ),
        # -------------------------------------------------------------------------------------------------------------
        # Funnel chart row
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id="funnel-sector", figure={})
                    ],
                    width=8),


                dbc.Col(
                    [
                        dcc.Graph(id="indicator-sector", figure={})
                    ],
                    width=4),
            ]
        ),
    ]
)

# -------------------------------------------------------------------------------------------------------------
# Callbacks


@app.callback(
    Output(component_id="date-picker-range-sector",
           component_property="min_date_allowed"),
    Output(component_id="date-picker-range-sector",
           component_property="max_date_allowed"),
    Output(component_id="date-picker-range-sector",
           component_property="initial_visible_month"),
    Output(component_id="date-picker-range-sector",
           component_property="start_date"),
    Output(component_id="date-picker-range-sector",
           component_property="end_date"),
    Input(component_id="dd-sector-multi", component_property="value")
)
def on_sector_dd_change(industries):
    sector_df = all_stock_df.loc[all_stock_df["Industry"].isin(industries)]
    min_date = sector_df["Date"].min()
    max_date = sector_df["Date"].max()

    return min_date, max_date, max_date, min_date, max_date


@app.callback(
    Output(component_id="graph-sector", component_property="figure"),
    Output(component_id="gauge-sector", component_property="value"),
    Output(component_id="funnel-sector", component_property="figure"),
    Output(component_id="indicator-sector",
           component_property="figure"),
    Input(component_id="btn-sector-run",
          component_property="n_clicks"),
    State(component_id="switch-percent-sector", component_property="on"),
    State(component_id="dd-sector-multi", component_property="value"),
    State(component_id="date-picker-range-sector",
          component_property="start_date"),

    State(component_id="date-picker-range-sector",
          component_property="end_date"),
    prevent_initial_call=True
)
# -------------------------------------------------------------------------------------------------------------
# Graphs
def on_apply_changes(n_clicks, percentOn, industries, start_date, end_date):
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)
# -------------------------------------------------------------------------------------------------------------
    # Sector Graph
    selected_industry_df = all_stock_df.loc[all_stock_df["Industry"].isin(
        industries)]
    selected_industry_df = selected_industry_df.loc[(selected_industry_df["Date"] >= start_datetime) & (
        selected_industry_df["Date"] <= end_datetime)]
    sector_df = all_stock_df.groupby(["Industry", "Date"]).mean()
    sector_fig = go.Figure(layout=go.Layout(
        title=go.layout.Title(text="Sectors"), shapes=[dict(
            x0=date, x1=date, y0=0, y1=1, xref='x', yref='paper',
            line_width=2) for date in selected_industry_df.drop_duplicates('Prime minister', keep="first")["Date"]],
        annotations=[dict(
            x=data[1]["Date"], y=0.05, xref='x', yref='paper',
            showarrow=False, xanchor='left', text=data[1]["Prime minister"]) for data in selected_industry_df.drop_duplicates('Prime minister', keep="first").iterrows()]
    ))
    for industry in industries:
        data = sector_df.loc[industry].reset_index()
        data["Date"] = data["Date"].dt.strftime('%Y-%m-%d')
        sector_fig.add_trace(go.Scatter(x=data["Date"], y=data["Percent change" if percentOn else "Close"],
                                        mode='lines',
                                        name=industry))
    sector_fig.update_xaxes(rangeslider_visible=True)

# -------------------------------------------------------------------------------------------------------------
    # Gauge chart
    date_wise_mean_df = selected_industry_df.groupby(
        by="Date").mean().reset_index()
    perc_change_start = date_wise_mean_df.iloc[0]["Close"]
    perc_change_end = date_wise_mean_df.iloc[-1]["Close"]
    gauge_value = 3 if perc_change_end > perc_change_start else 1

# -------------------------------------------------------------------------------------------------------------
    # Funnel chart
    funnel_fig = go.Figure()
    finance_minister_list = selected_industry_df["Finance minister"].unique()
    trade_sum_df = selected_industry_df.groupby(
        ["Industry", "Finance minister"]).sum().sort_values(by="Trades", ascending=False)
    for industry in industries:
        funnel_fig.add_trace(go.Funnel(
            name=industry,
            orientation="h",
            y=finance_minister_list,
            x=list(trade_sum_df.loc[industry].Trades),
            textposition="inside",
            textinfo="percent total"))
# -------------------------------------------------------------------------------------------------------------
    # Indicator
    indicator_fig = go.Figure()
    max_row = date_wise_mean_df.iloc[date_wise_mean_df['Percent change'].idxmax(
    )]
    min_row = date_wise_mean_df.iloc[date_wise_mean_df['Percent change'].idxmin(
    )]
    indicator_fig.add_trace(go.Indicator(
        mode="number+delta",
        value=max_row["Close"],
        title={"text": "{}<br><span style='font-size:0.8em;color:gray'>Best performance Day</span>".format(
            max_row["Date"].strftime('%Y-%m-%d'))},
        delta={'reference': max_row["Open"], 'relative': True},
        domain={'x': [0.5, 1], 'y': [0, 0.4]},))

    indicator_fig.add_trace(go.Indicator(
        mode="number+delta",
        value=min_row["Close"],
        title={"text": "{}<br><span style='font-size:0.8em;color:gray'>Worst performance Day</span>".format(
            min_row["Date"].strftime('%Y-%m-%d'))},
        delta={'reference': min_row["Open"], 'relative': True},
        domain={'x': [0.5, 1], 'y': [0.6, 1]},))

    return sector_fig, gauge_value, funnel_fig, indicator_fig
