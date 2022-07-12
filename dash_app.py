# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
from dash import Dash, dash_table, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.read_csv("spray_xwoba.csv")
df = df.round(3)
df.index = range(1, len(df) + 1)
names = df.batter_name.unique().tolist()


pitch_data = pd.read_csv("bbe.csv")

fig = px.scatter(df, x="xwoba", y="spray xwoba", color="diff", hover_data=["batter_name", "pa"], height=600, width=700)

field_swoba = px.density_heatmap(pitch_data,
 x='field_x',
  y="field_y",
   z="rf_spray_xwoba",
    histfunc="avg",
    height=600,
    width=600)
fig.update_yaxes(
    scaleanchor = "x",
    scaleratio = 1,
  )

field_swoba.add_hline(y=0, line_color="yellow")
field_swoba.add_vline(x=0, line_color="yellow")
field_swoba.layout.coloraxis.colorbar.title = "sexwOBA"
field_swoba.update_yaxes(
    scaleanchor = "x",
    scaleratio = 1,
  )

field_xwoba = px.density_heatmap(pitch_data,
 x='field_x',
  y="field_y",
   z="estimated_woba_using_speedangle",
    histfunc="avg",
    height=600,
    width=600)
field_xwoba.add_hline(y=0, line_color="yellow")
field_xwoba.add_vline(x=0, line_color="yellow")
field_xwoba.layout.coloraxis.colorbar.title = "xwOBA"
field_xwoba.update_yaxes(
    scaleanchor = "x",
    scaleratio = 1)

PAGE_SIZE = 10



app.layout = html.Div([
    html.H1(children='sexwOBA: spray angle enhanced xwOBA'),
    dcc.Slider(df['pa'].min(),
        df['pa'].max(),
        step=None,
        value=100,
        marks=None,
        tooltip={"placement": "bottom", "always_visible": True},
        id='pa-slider'),
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="single",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size=PAGE_SIZE,
    ),
    html.Div(id='datatable-interactivity-container'),
    html.H1(children='comparing xwoba and sexwoba'),
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label':i, 'value':i} for i in df['batter_name'].unique()
        ]),
    dcc.Graph(
        id='example-graph',
        figure=fig
    ),
    html.H1(children='field plots'),
    html.Div(children=[
        dcc.Graph(id='swoba-graph',
        style={'display': 'inline-block'},
        figure=field_swoba),
        dcc.Graph(id='xwoba-graph',
        style={'display': 'inline-block'},
        figure=field_xwoba)]),
])
@app.callback(Output('output', 'children'),
          [Input('dropdown', 'value')])
def update_output(value):
    filtered_df = df[df['batter_name'] == value]
    return filtered_df.iloc[0]['batter_name']

@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)

def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(
    Output('datatable-interactivity-container', "children"),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows")
)

def update_graphs(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncrasy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dff["batter_name"],
                        "y": dff[column],
                        "type": "bar",
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": column}
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        for column in ["diff"] if column in dff
    ]
@app.callback(
    Output('datatable-interactivity', 'figure'),
    Input('pa-slider', 'value'))

def update_table(selected_pa):
    filtered_df = df[df.pa >= selected_pa]

    fig = dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
        ],
        data=filtered_df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="single",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size=PAGE_SIZE,
    )

    fig.update_layout(transition_duration=500)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host = '127.0.0.1', dev_tools_hot_reload=False)
