from dash import Dash, dash_table, html, callback, Output, Input, no_update, State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import plotly.express as px
import pandas as pd

#Step1. Data Import
df = pd.read_csv('D:\\Sangwoo\\00.자기관리_인생계획\\자기관리_인생계획\\2.부동산공부\\00.연구자료\\data\\meme_all_data.csv')
#df = pd.read_csv('/home/ubuntu/source_data/meme_all_data.csv')

df = df.astype({'price':'int64'})
year_aixs = [y for y in range(2006,2023)]

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

#Step2. Dash Class
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.icons.FONT_AWESOME, dbc_css])
app.title = "APT Trading Insight"
server = app.server

#Step3. Dash Components
header = html.H1(
    "Korea Apartment Trading Volum", style={'textAlign':'center'}
)

dropdown_si = html.Div(
    [
        dbc.Label("Select City"),
        dcc.Dropdown(
            id="filter-city",
            options=[
                {"label": city, "value": city}
                for city in df.city.unique()
            ],
        ),
    ],
)

dropdown_gu = html.Div(
    [
        dbc.Label("Select Second Add"),
        dcc.Dropdown(
            id="filter-gu",
        ), 
    ],
)

dropdown_dong = html.Div(
    [
        dbc.Label("Select third Add"),
        dcc.Dropdown(
            id="filter-dong",
        ),
    ],
)

dropdown_year = html.Div(
    [
        dbc.Label("Select Years"),
        dcc.Dropdown(
            id = "filter-year",
            options = [{"label": year, "value": year} for year in df.year.unique()]
            )
    ]
)

graph_contents = html.Div(
    dcc.Graph(id='graph-content')
    )

datatable_contents = html.Div(
    [
        html.Div(id = 'title-datatable'),
        html.Div(
            dash_table.DataTable(
                id = 'datatable-top10',
                page_size=10,
                filter_action='native',
            )
        )
    ]
)

#step4 Dash Layout
app.layout = dbc.Container(
    [
        header,
        html.Hr(),
        dbc.Row([
            dbc.Col(dropdown_si),
            dbc.Col(dropdown_gu),
            dbc.Col(dropdown_dong)
        ],className="g-0"),
        dbc.Row([
            dbc.Col([graph_contents],md=8), #그래프
            dbc.Col([ 
                dbc.Row([dropdown_year]), #연도
                dbc.Row([datatable_contents]), #테이블
             ],md=4),            
        ],className="g-0"),
    ],
)

#Step5 Callbacks
@callback(
    Output("filter-gu",'options'),
    [Input("filter-city",'value')],
)
def update_gu(city):
    return [{"label": gu, "value": gu} for gu in df[df['city']==city].gu.unique()]

@callback(
    Output("filter-dong",'options'),
    Input("filter-gu",'value')
)
def update_dong(gu):
    return [{"label": dong, "value": dong} for dong in df[df['gu']==gu].dong.unique()]

@callback(
    Output('graph-content', 'figure'),
    Input('datatable-top10', 'active_cell'),
    [
        State('filter-city', 'value'),
        State('filter-gu', 'value'),
        State('filter-dong', 'value'),
        State('datatable-top10', 'data'),
    ]
)
def update_graph(active_cell,city,gu,dong,data):
    
    if active_cell is None:
        return no_update
    else:
        row_id = active_cell['row_id']
        
        search_data = [ item for item in data if item['id']==row_id][0]
        apt_py = search_data['apt_py']
    
        mask = (
            (df.city == city)
            & (df.gu == gu)
            & (df.apt_py == apt_py)
        )
                
    filtered_df = df.loc[mask, :]
    groupby_df = pd.DataFrame(filtered_df.groupby(['year'],as_index=0)['apt'].count())

    max_data = groupby_df['apt'].max()
    if max_data >= 200:
        max_y = max_data+50
    elif max_data >=150:
        max_y = 200
    elif max_data >=100:
        max_y= 150
    elif max_data >=50:
        max_y= 100
    elif max_data >=30:
        max_y= 50
    else:
        max_y= 30

    fig = px.bar(groupby_df, x='year', y='apt', title=apt_py)
    fig.update_xaxes(range=[2005,2024])
    fig.update_yaxes(range=[0,max_y])

    return fig

@callback(
    [Output('datatable-top10', 'columns'), 
     Output('datatable-top10', 'data'),
     Output('datatable-top10','style_cell_conditional'),
     Output('title-datatable','children')],
    [Input('filter-dong', 'value'),
     Input('filter-gu', 'value'),
     Input('filter-year','value')],
    [State('filter-city', 'value'),]
)
def update_datatable(dong,gu,year,city):

    if year is None:
        year = 2023

    if dong is None:
        mask = (
            (df.city == city)
            & (df.gu == gu)
            & (df.year == year)
        )
    else:
        mask = (
            (df.city == city)
            & (df.gu == gu)
            & (df.dong == dong)
            & (df.year == year)
        )

    filtered_df = df.loc[mask, :]

    groupby_df = (
        pd.DataFrame(filtered_df.groupby(['apt_py'])['apt'].count().reset_index(name='apt'))
                  .sort_values(by = 'apt', ascending = False)
    )
    groupby_df.index.name = 'id'    
    groupby_df.reset_index(inplace=True)

    cols = [
        {"name": i, "id": i} for i in groupby_df.columns
    ]
    
    style_cell_conditional = [
        {
            'if': {'column_id': 'id'},
            'display': 'none'
        }
    ]

    year_title = "Rank in " + str(year)

    return cols, groupby_df.to_dict('records'),style_cell_conditional, year_title
    
#Step6 Run App
if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0',port=8050)