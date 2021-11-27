import plotly.express as px
from dash import html
from dash import dcc
import dash_daq as daq
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
from app import app
import plotly.graph_objects as go
from data import all_stock_df, industries
# -------------------------------------------------------------------------------------------------------------
# Stock tab Layout
stocks_layout = html.Div(
    [
        # -------------------------------------------------------------------------------------------------------------
        # Dropdown row
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Select Sector"),
                        dcc.Dropdown(
                            id="dd-sector-single",
                            multi=False,
                            value=list(industries.keys())[0],
                            options=[
                                {"label": industry, "value": industry}
                                for industry in industries.keys()
                            ],
                            clearable=False,
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        html.Label("Select Stocks"),
                        dcc.Dropdown(
                            id="dd-stock-multi",
                            multi=True,
                            value="",
                            options=[],
                            clearable=False,
                        ),
                    ],
                    width=5,
                ),
                dbc.Col(
                    [
                        html.Label("Select Date Range"),
                        dcc.DatePickerRange(
                            id='date-picker-range-stock',
                        )
                    ],
                    width=4,
                ),
                dbc.Row(
                    [
                        dbc.Col([daq.BooleanSwitch(
                            id="switch-candle-stock",
                            label='Candle stick',
                            labelPosition='bottom'
                        )], style={"paddingLeft": "2rem", "paddingTop": "1rem"}),
                        dbc.Col([
                            daq.BooleanSwitch(
                                id="switch-percent-stock",
                                label='Percent change',
                                labelPosition='bottom'
                            )], style={"paddingLeft": "2rem", "paddingTop": "1rem"}),
                        dbc.Button("Apply changes", color="info",
                                   className="mr-1", id="btn-stock-run", style={"margin": "2rem"}),
                    ]),
            ],
            className="mt-4",

        ),
        # -------------------------------------------------------------------------------------------------------------
        # Stock graph row
        dbc.Row(
            [

                dbc.Col(
                    [
                        dcc.Graph(id="graph-stock", figure={}),
                        dbc.Row([
                            html.H6("Rolling mean",
                                    style={"textAlign": "center", "padding": "1rem"})
                        ]),
                        dcc.Slider(
                            id='slider-moving-average',
                            min=1,
                            max=100,
                            step=1,
                            value=1,
                            tooltip={"placement": "top"}
                        )
                    ],
                    width=8),


                dbc.Col(
                    [
                        daq.Gauge(
                            style={"marginTop": "6rem"},
                            id='gauge-stock',
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
        # Radar chart row
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id="radar-stock", figure={})
                    ],
                    width=7),


                dbc.Col(
                    [
                        dcc.Graph(id="indicator-stock", figure={})
                    ],
                    width=5),
            ]
        ),
    ]
)

# -------------------------------------------------------------------------------------------------------------
# Callbacks


@app.callback(
    Output(component_id="dd-stock-multi", component_property="options"),
    Output(component_id="dd-stock-multi", component_property="value"),
    Input(component_id="dd-sector-single", component_property="value")
)
def on_sector_dd_change(industry):
    sector_df = all_stock_df.loc[all_stock_df["Industry"] == industry]
    stocks = [stock for stock in sector_df["Symbol"].unique()]
    stock_options = [{"label": stock, "value": stock}for stock in stocks]

    return stock_options, stocks


@app.callback(
    Output(component_id="date-picker-range-stock",
           component_property="min_date_allowed"),
    Output(component_id="date-picker-range-stock",
           component_property="max_date_allowed"),
    Output(component_id="date-picker-range-stock",
           component_property="initial_visible_month"),
    Output(component_id="date-picker-range-stock",
           component_property="start_date"),
    Output(component_id="date-picker-range-stock",
           component_property="end_date"),
    Input(component_id="dd-stock-multi", component_property="value")
)
def on_stock_dd_change(stocks):
    stocks_df = all_stock_df.loc[all_stock_df["Symbol"].isin(stocks)]
    min_date = stocks_df["Date"].min()
    max_date = stocks_df["Date"].max()

    return min_date, max_date, max_date, min_date, max_date


@app.callback(
    Output(component_id="switch-percent-stock", component_property="disabled"),
    Output(component_id="slider-moving-average",
           component_property="disabled"),
    Input(component_id="switch-candle-stock", component_property="on"),
    State(component_id="dd-stock-multi", component_property="value"),
    prevent_initial_call=True
)
def on_switch_candle_change(isOn, stocks):

    return isOn, isOn


@app.callback(
    Output(component_id="graph-stock", component_property="figure"),
    Output(component_id="gauge-stock", component_property="value"),
    Output(component_id="radar-stock", component_property="figure"),
    Output(component_id="indicator-stock",
           component_property="figure"),
    Input(component_id="btn-stock-run",
          component_property="n_clicks"),
    State(component_id="switch-candle-stock", component_property="on"),
    State(component_id="switch-percent-stock", component_property="on"),
    State(component_id="slider-moving-average",
          component_property="value"),
    State(component_id="dd-sector-single", component_property="value"),
    State(component_id="dd-stock-multi", component_property="value"),
    State(component_id="date-picker-range-stock",
          component_property="start_date"),

    State(component_id="date-picker-range-stock",
          component_property="end_date"),
    prevent_initial_call=True
)
# -------------------------------------------------------------------------------------------------------------
# Graphs
def on_apply_changes(n_clicks, candle_on, percent_on, moving_average_value, industry, stocks, start_date, end_date):
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)
# -------------------------------------------------------------------------------------------------------------
    # Stock Graph

    selected_stock_df = all_stock_df.loc[all_stock_df["Symbol"].isin(stocks)]
    selected_stock_df = selected_stock_df.loc[(selected_stock_df["Date"] >= start_datetime) & (
        selected_stock_df["Date"] <= end_datetime)]

    if candle_on:
        candle_stock_df = selected_stock_df.loc[selected_stock_df["Symbol"] == stocks[0]]
        stock_fig = go.Figure(data=[go.Candlestick(x=candle_stock_df['Date'],
                                                   open=candle_stock_df['Open'], high=candle_stock_df['High'],
                                                   low=candle_stock_df['Low'], close=candle_stock_df['Close']),
                                    ], layout=go.Layout(
            title=go.layout.Title(text=stocks[0]), shapes=[dict(
                x0=date, x1=date, y0=0, y1=1, xref='x', yref='paper',
                line_width=2) for date in candle_stock_df.drop_duplicates('Prime minister', keep="first")["Date"]],
            annotations=[dict(
                x=data[1]["Date"], y=0.05, xref='x', yref='paper',
                showarrow=False, xanchor='left', text=data[1]["Prime minister"]) for data in candle_stock_df.drop_duplicates('Prime minister', keep="first").iterrows()]
        ))
    else:
        selected_stock_df["Rolling mean"] = selected_stock_df["Percent change" if percent_on else "Close"].rolling(
            window=moving_average_value).mean()
        stock_fig = px.line(selected_stock_df, title=industry, x="Date", y="Rolling mean", color="Symbol",
                            line_group="Symbol", hover_name="Symbol", line_shape="spline", render_mode="svg")
        for data in selected_stock_df.drop_duplicates('Prime minister', keep="first").iterrows():
            stock_fig.add_annotation(x=data[1]["Date"], y=0.05,
                                     text=data[1]["Prime minister"],)
    stock_fig.update_xaxes(rangeslider_visible=True)

# -------------------------------------------------------------------------------------------------------------
    # Gauge chart
    perc_change_start = selected_stock_df.loc[selected_stock_df["Date"] ==
                                              start_datetime, "Close"].mean()
    perc_change_end = selected_stock_df.loc[selected_stock_df["Date"] ==
                                            end_datetime, "Close"].mean()
    gauge_value = 3 if perc_change_end > perc_change_start else 1
# -------------------------------------------------------------------------------------------------------------
    # Radar chart
    radar_fig = go.Figure()
    radar_categories = selected_stock_df["Finance minister"].unique()
    for stock in stocks:
        radar_fig.add_trace(go.Scatterpolar(
            r=selected_stock_df.loc[selected_stock_df["Symbol"]
                                    == stock].groupby(by="Finance minister").mean()["Percent change"],
            theta=radar_categories,
            fill='toself',
            name=stock
        ))
# -------------------------------------------------------------------------------------------------------------
    # Indicators

    data_dict = {"Symbol": [], "Initial close": [], "Final close": []}

    for stock in stocks:
        if stock not in selected_stock_df["Symbol"].unique():
            continue
        data_dict["Symbol"].append(stock)
        stock_df = selected_stock_df.loc[selected_stock_df["Symbol"] == stock]
        data_dict["Initial close"].append(stock_df.iloc[0]["Close"])
        data_dict["Final close"].append(stock_df.iloc[-1]["Close"])
    data_df = pd.DataFrame.from_dict(data_dict)
    data_df["Diff"] = data_df["Final close"] - data_df["Initial close"]
    data_df = data_df.sort_values(by=["Diff"])

    indicator_fig = go.Figure()
    indicator_fig.add_trace(go.Indicator(
        mode="number+delta",
        value=data_df.iloc[-1]["Final close"],
        title={"text": "{}<br><span style='font-size:0.8em;color:gray'>Best performing Stock</span>".format(
            data_df.iloc[-1]["Symbol"])},
        delta={'reference': data_df.iloc[-1]
               ["Initial close"], 'relative': True},
        domain={'x': [0.5, 1], 'y': [0, 0.5]},))

    indicator_fig.add_trace(go.Indicator(
        mode="number+delta",
        value=data_df.iloc[0]["Final close"],
        title={"text": "{}<br><span style='font-size:0.8em;color:gray'>Worst performing Stock</span>".format(
            data_df.iloc[0]["Symbol"])},

        delta={'reference': data_df.iloc[0]
               ["Initial close"], 'relative': True},
        domain={'x': [0.5, 1], 'y': [0.5, 1]},))

    return stock_fig, gauge_value, radar_fig, indicator_fig
