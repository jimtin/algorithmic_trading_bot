import plotly.graph_objects as go
from dash import Dash, html, dcc
from plotly.subplots import make_subplots


# Function to display a plotly graph in dash
def display_graph(plotly_fig, graph_title, dash=False):
    """
    Function to display a plotly graph using Dash
    :param plotly_fig: plotly figure
    :param graph_title: string
    :param dash: boolean to determine whether to run the dash server
    :return: None
    """
    # Add in layout features for each plotly figure
    plotly_fig.update_layout(
        xaxis_rangeslider_visible=False,
        autosize=True,
        height=800
    )
    plotly_fig.update_yaxes(automargin=True)

    if dash:
        # Create the Dash object
        app = Dash(__name__)
        # Construct view
        app.layout = html.Div(children=[
            html.H1(children=graph_title),
            html.Div("Created by James Hinton from AlgoQuant.Trade"),
            dcc.Graph(
                id=graph_title,
                figure=plotly_fig
            )
        ])
        # Run the image
        app.run_server(debug=True)
    else:
        plotly_fig.show()


# Function to display a backtest
def display_backtest(proposed_trades, completed_trades, win_objects, loss_objects, proposed_trades_table, indicators=[],
                     graph_title="Backtest"):
    # Todo: add callback so that trailing stops can be explored
    # Create a Dash Object
    app = Dash(__name__)

    # Construct view
    app.layout = html.Div(children=[
        html.H1(graph_title),
        html.Div([
            html.H1(children="Strategy With Trades"),
            html.Div(children='''Original Strategy'''),
            dcc.Graph(
                id="strat_with_trades",
                figure=completed_trades,
                style={'height': '100vh'}
            )
        ]),
        html.Div([
            html.H1(children="Strategy With Proposed Trades"),
            html.Div(children='''Original Strategy'''),
            dcc.Graph(
                id="display_trades",
                figure=proposed_trades
            )
        ]),
        html.Div([
            html.H1(children="Proposed Trades Table"),
            html.Div(children='''Original Strategy'''),
            dcc.Graph(
                id="table_trades",
                figure=proposed_trades_table
            )
        ]),
        html.Div([
            html.H1(children="Win Objects"),
            html.Div(children='''Win Objects'''),
            dcc.Graph(
                id="win_objects",
                figure=win_objects
            )
        ]),
        html.Div([
            html.H1(children="Loss Objects"),
            html.Div(children='''Loss Objects'''),
            dcc.Graph(
                id="loss_objects",
                figure=loss_objects
            )
        ])
    ])

    app.run_server(debug=True)



# Function to construct base candlestick graph
def construct_base_candlestick_graph(dataframe, candlestick_title):
    """
    Function to construct base candlestick graph
    :param candlestick_title: String
    :param dataframe: Pandas dataframe object
    :return: plotly figure
    """
    # Construct the figure
    fig = go.Figure(data=[go.Candlestick(
        x=dataframe['human_time'],
        open=dataframe['open'],
        high=dataframe['high'],
        close=dataframe['close'],
        low=dataframe['low'],
        name=candlestick_title
    )])
    # Return the graph object
    return fig


# Function to add a histogram to a plot
def add_histogram_to_graph(base_fig, dataframe, dataframe_column, histogram_name):
    """
    Function to add a histogram to an existing plotly figure
    :param base_fig: plotly figure object
    :param dataframe: pandas dataframe
    :param dataframe_column: string of column to plot
    :param histogram_name: string title of histogram
    :return: updated plotly figure
    """
    # Construct trace
    base_fig.add_trace(go.Histogram(
        x=dataframe['human_time'],
        y=dataframe[dataframe_column],
        name=histogram_name
    ))
    # Return the object
    return base_fig


# Function to add a bar chart to plot
def add_bar_to_graph(base_fig, dataframe, dataframe_column, bar_name, layer=False, candlestick_title=""):
    """
    Function to add a bar chart to an existing plotly figure
    :param base_fig: plotly figure object
    :param dataframe: pandas dataframe
    :param dataframe_column: string of column to plot
    :param bar_name: string title of bar chart
    :return: updated plotly figure
    """

    if layer:
        # Create a new figure
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        # Add the raw candlesticks
        fig2 = fig2.add_trace(
            go.Candlestick(
                x=dataframe['human_time'],
                open=dataframe['open'],
                high=dataframe['high'],
                close=dataframe['close'],
                low=dataframe['low'],
                name=candlestick_title
            ),
            secondary_y=False
        )
        # Construct trace
        fig2.add_trace(
            go.Bar(
                x=dataframe['human_time'],
                y=dataframe[dataframe_column],
                name=bar_name,
            ),
            secondary_y=True
        )
        return fig2
    else:
        # Construct trace
        base_fig.add_trace(go.Bar(
            x=dataframe['human_time'],
            y=dataframe[dataframe_column],
            name=bar_name
        ))
        # Return the object
        return base_fig


# Function to display a MACD indicator
def display_macd_indicator(dataframe, title):
    """
    Function to display a MACD indicator
    :param dataframe: dataframe with all values
    :param title: Title of the data
    :return: figure with all data
    """
    # Set up the figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add in the candlesticks for the original data
    fig = fig.add_trace(
        go.Candlestick(
            x=dataframe['human_time'],
            open=dataframe['open'],
            high=dataframe['high'],
            close=dataframe['close'],
            low=dataframe['low'],
            name=title
        ),
        secondary_y=False
    )
    # Add in the MACD line
    fig = fig.add_trace(
        go.Scatter(
            x=dataframe['human_time'],
            y=dataframe['macd'],
            name="MACD"
        ),
        secondary_y=True
    )
    # Add in the MACD signal line
    fig = fig.add_trace(
        go.Scatter(
            x=dataframe['human_time'],
            y=dataframe['macd_signal'],
            name="MACD Signal"
        ),
        secondary_y=True
    )
    # Add in the MACD histogram
    fig = fig.add_trace(
        go.Bar(
            x=dataframe['human_time'],
            y=dataframe['macd_histogram'],
            name="MACD Histogram"
        ),
        secondary_y=True
    )
    return fig


# Function to display a RSI indicator
def display_rsi_indicator(dataframe, title):
    """
    Function to display a RSI indicator
    :param dataframe: dataframe with price data and rsi
    :param title: Symbol for title
    :return: figure with all data
    """
    # Set up the figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add in the candlesticks for the original data
    fig = fig.add_trace(
        go.Candlestick(
            x=dataframe['human_time'],
            open=dataframe['open'],
            high=dataframe['high'],
            close=dataframe['close'],
            low=dataframe['low'],
            name=title
        ),
        secondary_y=False
    )
    # Add in the RSI line
    fig = fig.add_trace(
        go.Scatter(
            x=dataframe['human_time'],
            y=dataframe['rsi'],
            name="RSI"
        ),
        secondary_y=True
    )
    return fig


# Function to add a line trace to a plot
def add_line_to_graph(base_fig, dataframe, dataframe_column, line_name):
    """
    Function to add a line to trace to an existing figure
    :param base_fig: plotly figure object
    :param dataframe: pandas dataframe
    :param dataframe_column: string of column to plot
    :param line_name: string title of line trace
    :return: updated plotly figure
    """
    # Construct trace
    base_fig.add_trace(go.Scatter(
        x=dataframe['human_time'],
        y=dataframe[dataframe_column],
        name=line_name
    ))
    # Return the object
    return base_fig


# Function to display points on graph as diamond
def add_markers_to_graph(base_fig, dataframe, value_column, point_names):
     """
     Function to add points to a graph
     :param base_fig: plotly figure
     :param dataframe: pandas dataframe
     :param value_column: value for Y display
     :param point_names: what's being plotted
     :return: updated plotly figure
     """
     # Construct trace
     base_fig.add_trace(go.Scatter(
         mode="markers",
         marker=dict(size=8, symbol="diamond"),
         x=dataframe['human_time'],
         y=dataframe[value_column],
         name=point_names
     ))
     return base_fig


# Function to turn a dataframe into a table
def add_proposed_trades_to_graph(dataframe):
    fig = go.Figure(data=[go.Table(
            header=dict(values=["Time", "Order Type", "Stop Price", "Stop Loss", "Take Profit"], align='left'),
            cells=dict(values=[
                dataframe['human_time'],
                dataframe['order_type'],
                dataframe['stop_price'],
                dataframe['stop_loss'],
                dataframe['take_profit']
            ])
        )]
    )
    return fig


# Function to add trades to graph
def add_trades_to_graph(proposed_trades_dataframe, base_fig):
    # Create a point plot list
    point_plot = []
    # Create the colors
    buy_color = "blue"
    sell_color = "purple"
    # Add each set of trades
    for index, row in proposed_trades_dataframe.iterrows():
        # Set the colour
        if row['order_type'] == "BUY_STOP":
            color = buy_color
        else:
            color = sell_color
        # Add in the stop loss and take profit
        base_fig.add_shape(
            type="rect",
            x0=row['human_time'],
            y0=row['stop_loss'],
            x1=row['cancel_time'],
            y1=row['take_profit'],
            line=dict(
                color=color,
                width=2
            )
        )
        """
        # Add in the stop price
        base_fig.add_shape(
            type="line",
            x0=row['human_time'],
            x1=row['human_time'],
            y0=row['stop_price'],
            line=dict(
                color=color,
                width=2
            )
        )
        """
        base_fig.update_layout(
            xaxis_rangeslider_visible=False,
            autosize=True,
        )
    return base_fig


# Function to add proposed trades to graph
def proposed_trades_graph(raw_candlesticks, proposed_trades):
    # Plot the underlying candlesticks
    fig = construct_base_candlestick_graph(raw_candlesticks, "Proposed Trades")
    # Overlay the trades
    fig = add_trades_to_graph(proposed_trades, fig)
    # Return the figure
    return fig


# Function to add display backtest outcomes
def completed_trades(raw_candles, backtest_results):
    # Construct the base trade results
    fig = construct_base_candlestick_graph(raw_candles, "Completed Trades")
    # Add in layout features for each plotly figure
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        autosize=True,
    )
    fig.update_yaxes(automargin=True)
    # Extract the winning Trades
    winning_trades = backtest_results['win_objects']
    # Iterate through each winning trade and add it to the plot
    for index, trade in enumerate(winning_trades):
        if index == 0:
            fig = fig.add_trace(
                go.Scatter(
                    x=[trade['trade_open_time'], trade['closing_time']],
                    y=[trade['closing_stop_price'], trade['closing_price']],
                    name="Winning Trades",
                    legendgroup="winning_trades",
                    line=dict(color="blue")
                )
            )
        else:
            fig = fig.add_trace(
                go.Scatter(
                    x=[trade['trade_open_time'], trade['closing_time']],
                    y=[trade['closing_stop_price'], trade['closing_price']],
                    name="Winning Trades",
                    legendgroup="winning_trades",
                    line=dict(color="blue"),
                    showlegend=False
                )
            )
    # Extract the losing Trades
    losing_trades = backtest_results['loss_objects']
    # Iterate through each losing trade and add it to the plot
    for index, trade in enumerate(losing_trades):
        if index == 0:
            fig = fig.add_trace(
                go.Scatter(
                    x=[trade['trade_open_time'], trade['closing_time']],
                    y=[trade['closing_stop_price'], trade['closing_price']],
                    name="Losing Trades",
                    legendgroup="losing_trades",
                    line=dict(color="red")
                )
            )
        else:
            fig = fig.add_trace(
                go.Scatter(
                    x=[trade['trade_open_time'], trade['closing_time']],
                    y=[trade['closing_stop_price'], trade['closing_price']],
                    name="Losing Trades",
                    legendgroup="losing_trades",
                    line=dict(color="red"),
                    showlegend=False
                )
            )
    # Return the figure
    return fig


# Convert a dataframe into a table
def dataframe_to_table(dataframe, title):
    """
    Function to convert a dataframe into a table
    :param dataframe: dataframe of the data to be plotted
    :param title: string of the title of the dataframe
    :return: figure with table
    """
    # Create the figure
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(dataframe.columns), align='left'),
        cells=dict(values=[dataframe[col] for col in dataframe.columns], align='left')
    )])
    # Add in the title
    fig.update_layout(title_text=title)
    # Return the figure
    return fig
