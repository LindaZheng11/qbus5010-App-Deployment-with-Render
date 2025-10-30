# 导入库
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np

app = Dash(__name__)

server = app.server
# =========================== THEME==========================
THEME = {
    "bg_page": "#F8F3E9",      
    "bg_card": "white",        
    "font": "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, 'Apple Color Emoji','Segoe UI Emoji'",
    "text": "#1f2937",        
    "muted": "#6b7280",        
    "categorical": ["#2F7DD1", "#E45756", "#3A86FF", "#2FBF71", "#9B59B6", "#FF9F1C", "#2E86AB", "#7FB069"],
    "series_primary": "#2F7DD1",
    "series_accent":  "#E45756",
    "choropleth_scale": ["#FFF5EC", "#FFDDBE", "#FFBE8F", "#FF995E", "#FF7A3A", "#E4572E"],
    "geo": {
        "land":   "#F9FAFB",
        "ocean":  "#E6F0FA",
        "lake":   "#DDEBFA",
        "border": "#475569",
        "coast":  "#94A3B8",
        "frame":  False
    }
}

# 注册 Plotly 模板（统一字体/网格/图例/分类色）——保持不变
pio.templates["apricot"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family=THEME["font"], color=THEME["text"], size=14),
        title=dict(font=dict(size=20, color=THEME["text"])),
        legend=dict(
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(0,0,0,0)",
            orientation="h", x=0.5, xanchor="center", y=-0.15, yanchor="top"
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#e9edf2", zeroline=False, showline=False),
        yaxis=dict(gridcolor="#e9edf2", zeroline=False, showline=False),
        colorway=THEME["categorical"]
    )
)
pio.templates.default = "apricot"

# --------------------------- 公共样式 ---------------------------
CARD = {'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '14px',
        'boxShadow': '0 8px 32px rgba(0,0,0,0.06)'}
CONTAINER = {"maxWidth": "1200px", "margin": "0 auto", "padding": "12px"}
GRID = {'display': 'grid', 'gridTemplateColumns': '58% 42%', 'gap': '20px',
        "maxWidth": "1200px", "margin": "20px auto"}

# DataTable 统一外观（两张表共用）
TABLE_STYLE_ARGS = dict(
    style_table={'width': '100%', 'margin': 'auto', 'overflowX': 'auto', 'border': 'none'},
    style_as_list_view=True,
    style_cell={
        'textAlign': 'left',
        'padding': '10px',      
        'border': 'none',
        'fontFamily': THEME["font"],
        'color': THEME["text"],
        'fontSize': 14,
        'backgroundColor': 'white',
        'whiteSpace': 'normal', 
        'height': 'auto',
        'minWidth': '80px',
        'lineHeight': '1.25',  
        'boxSizing': 'border-box'
    },
    style_header={
        'fontWeight': '700',
        'backgroundColor': '#1F3A5F',
        'color': 'white',
        'border': 'none',
        'padding': '12px 10px',
        'whiteSpace': 'normal',
        'lineHeight': '1.2'
    },
    style_cell_conditional=[
        {'if': {'column_id': 'University'}, 'minWidth': '280px'},
        {'if': {'column_id': 'Country'}, 'minWidth': '140px'}
    ],
    style_data_conditional=[
        {'if': {'row_index': 'odd'}, 'backgroundColor': '#FAFAFA'},
        {'if': {'state': 'active'}, 'backgroundColor': '#FFF4E8', 'border': 'none'},
        {'if': {'state': 'selected'}, 'backgroundColor': '#FFE7D1', 'border': 'none'},
    ],

    css=[{
        'selector': '.dash-cell div.dash-cell-value',
        'rule': 'display:inline; white-space:inherit; overflow:visible; text-overflow:clip;'
    }],
    tooltip_delay=0,
    tooltip_duration=None,
)

# --------------------------- Darren 数据 ---------------------------
df = pd.read_csv('Darren.csv')

# --------------------------- 雷达图数据（df2） ---------------------------
CSV_FILE = "Li.csv"
COLS = {
    "name": "University Name", "AR": "Academic Reputation SCORE",
    "ER": "Employer Reputation SCORE", "FSR": "Faculty Student SCORE",
    "CPF": "Citations per Faculty SCORE", "IFR": "International Faculty SCORE",
    "ISR": "International Faculty SCORE.1",
}
LABELS_FULL = ["Academic Reputation","Employer Reputation","Faculty Student Ratio",
               "Citations per Faculty","International Faculty","International Student"]
METRIC_KEYS = ["AR","ER","FSR","CPF","IFR","ISR"]
METRIC_COLS = [COLS[k] for k in METRIC_KEYS]

df2 = (pd.read_csv(CSV_FILE, usecols=[COLS["name"]] + METRIC_COLS)
         .rename(columns={**{COLS["name"]:"name"}, **{COLS[k]:k for k in METRIC_KEYS}}))
for k in METRIC_KEYS: df2[k] = pd.to_numeric(df2[k], errors="coerce")
df2 = df2.dropna(subset=["name"]).drop_duplicates("name")
universities = sorted(df2["name"].astype(str))
default1 = universities[0] if universities else None
default2 = universities[1] if len(universities) > 1 else default1

# --------------------------- 趋势图数据（df3） ---------------------------
df3 = pd.read_csv("Linda.csv", encoding="latin1").rename(columns={
    "2026 Rank":"Rank_2026","2025 Rank":"Rank_2025","2024 Rank":"Rank_2024",
    "2023 Rank":"Rank_2023","Name":"University","Country":"Country","Region":"Region"
})
df3 = df3[["Index","Rank_2026","Rank_2025","Rank_2024","Rank_2023","University","Country","Region"]]
df3 = df3.dropna(subset=["University"])
for c in ["Rank_2026","Rank_2025","Rank_2024","Rank_2023"]:
    df3[c] = pd.to_numeric(df3[c].astype(str).str.replace("=", "", regex=False), errors="coerce")
df3 = df3[df3["Rank_2026"] <= 50]
df3_long = (df3.melt(id_vars=["University","Country","Region"],
                     value_vars=["Rank_2023","Rank_2024","Rank_2025","Rank_2026"],
                     var_name="Year", value_name="Rank"))
df3_long["Year"] = df3_long["Year"].str.replace("Rank_","").astype(int)

# --------------------------- Layout ---------------------------
app.layout = html.Div([

    # ======= Page Header（已按你指定标题）=======
    html.Div([
        html.H1("QS-Based Analytics for Top Universities",
                style={
                    'fontFamily': THEME["font"],
                    'color': THEME["text"],
                    'fontWeight': 800,
                    'fontSize': '36px',
                    'letterSpacing': '-0.02em',
                    'margin': '4px 0 6px'
                }),
        html.P("Interactive insights across rankings, scores, geographies and trends (2023–2026)",
               style={
                   'color': THEME["muted"],
                   'fontSize': '16px',
                   'margin': '0 0 12px'
               }),
        html.Div(style={
            'height': '3px',
            'width': '100%',
            'background': THEME["series_primary"],
            'borderRadius': '2px',
            'opacity': 0.9,
            'margin': '4px 0 16px'
        })
    ], style={**CONTAINER, 'paddingTop': '6px'}),

    # === Darren 区域（打包成单卡片） ===
    html.Div([
        html.Div([
            html.Div([
                html.Label("Select Size:", style={'fontSize': '18px', 'fontWeight': '600', 'marginRight': '10px'}),
                dcc.RadioItems(
                    df['SIZE'].unique(),
                    value=200,
                    id='AAA',
                    inline=True,
                    inputStyle={'marginRight': '6px'},
                    labelStyle={'display': 'inline-block', 'marginRight': '14px', 'marginBottom': '8px'},
                    style={'marginTop': '2px'}
                )
            ], style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'alignItems': 'center',
                'gap': '4px',
                'margin': '0 0 12px 0',
                'textAlign': 'left'
            }),

            # 地图
            dcc.Graph(id='choropleth', style={"marginBottom": "12px"}),

            # 年份滑条（保留在地图下方）
            html.Div([
                html.Label("Select Year:", style={'fontSize': '18px', 'fontWeight': '600', 'display': 'block', 'marginBottom': '6px'}),
                dcc.Slider(
                    df['YEAR'].min(),
                    df['YEAR'].max(),
                    step=None,
                    value=df['YEAR'].max(),
                    marks={str(year): str(year) for year in df['YEAR'].unique()},
                    id='CCC'
                )
            ], style={"padding": "6px 14px 10px"})
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '14px',
            'boxShadow': '0 4px 24px rgba(0,0,0,0.05)'
        })
    ], style=CONTAINER),

    # 中部：左趋势 | 右雷达
    html.Div([
        html.Div([
            html.H2("Top 50 QS World University Rankings",
                    style={'textAlign':'center','fontWeight':700,'marginBottom':'12px'}),
            html.Label("Filter by Country:", style={'fontSize':16,'fontWeight':600}),
            dcc.Dropdown(id='country_dropdown',
                         options=[{'label':c,'value':c} for c in sorted(df3_long["Country"].unique())],
                         value="Australia", clearable=True, style={'marginBottom':'10px'}),
            html.Label("Select Universities:", style={'fontSize':16,'fontWeight':600}),
            dcc.Dropdown(id='university_dropdown',
                         options=[{'label':u,'value':u} for u in sorted(df3_long["University"].unique())],
                         value=[], multi=True),
            dcc.Graph(id='ranking_chart', style={'height':'600px','marginTop':'10px'})
        ], style=CARD),

        html.Div([
            html.H2("2026 QS 100 University Score Comparison",
                    style={"textAlign":"center","fontWeight":700,"marginBottom":"16px"}),
            html.Label("Select Universities:", style={'fontSize':16,'fontWeight':600}),
            dcc.Dropdown(id="uni1", options=universities, value=default1,
                         placeholder="University A", searchable=True, clearable=False,
                         style={'marginTop':'6px'}),
            html.Br(),
            dcc.Dropdown(id="uni2", options=universities, value=default2,
                         placeholder="University B", searchable=True, clearable=False),
            html.Br(),
            dcc.Graph(id="radar", style={"height":"600px","width":"100%","display":"block","margin":"0 auto"})
        ], style=CARD),
    ], style=GRID),

    # 年份/区域控件 + 表格
    html.Div([
        html.Label("Select Year:", style={'fontSize':18,'marginRight':'20px'}),
        dcc.RadioItems(id='year_radio',
                       options=[{'label':y, 'value':f'Rank_{y}'} for y in [2023,2024,2025,2026]],
                       value='Rank_2026', inline=True),
        html.Br(),
        html.Label("Select Region:", style={'fontSize':18}),
        dcc.Dropdown(id='region_dropdown',
                     options=[{'label':r,'value':r} for r in sorted(df3["Region"].unique())],
                     value="Europe", clearable=True, style={'width':'320px','margin':'8px auto 0'})
    ], style={'textAlign':'center','margin':'20px auto 10px'}),

    html.Div([
        html.Div([
            html.H3("Top 10 Universities in the world", style={'textAlign':'center'}),
            dash_table.DataTable(
                id='top10_table',
                **TABLE_STYLE_ARGS
            )
        ], style={'width':'49%','display':'inline-block','verticalAlign':'top'}),
        html.Div([
            html.H3("Region-selected Universities within Top 50", style={'textAlign':'center'}),
            dash_table.DataTable(
                id='region_table',
                **TABLE_STYLE_ARGS
            )
        ], style={'width':'49%','display':'inline-block','verticalAlign':'top'})
    ], style={'width':'100%','textAlign':'center','display':'flex','justifyContent':'space-between',
              **{"maxWidth":"1200px","margin":"10px auto 30px"}})

],
style={
    "backgroundColor": THEME["bg_page"],
    "minHeight": "100vh",
    "padding": "10px"
})

# --------------------------- Callbacks ---------------------------
@app.callback(Output("choropleth","figure"),
              Input("AAA","value"), Input("CCC","value"))
def update_map(AAA, CCC):
    f = df[(df['YEAR']==CCC) & (df['SIZE']==AAA)]

    fig = px.choropleth(
        f,
        locations="COUNTRY NAME",
        locationmode="country names",
        color="NUMBER",
        color_continuous_scale=THEME["choropleth_scale"],
        title=f"Distribution of Top Universities by Country in {CCC} (Size = {AAA})",
        template="apricot"
    )

    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Count",
            thickness=12,
            outlinewidth=0,
            ticks="outside"
        ),
        geo=dict(
            projection_type="equirectangular",
            showframe=THEME["geo"]["frame"],
            showcoastlines=True,
            showcountries=True,
            showlakes=True,
            showocean=True,
            coastlinecolor=THEME["geo"]["coast"],
            countrycolor=THEME["geo"]["border"],
            lakecolor=THEME["geo"]["lake"],
            oceancolor=THEME["geo"]["ocean"],
            bgcolor="white",
            landcolor=THEME["geo"]["land"]
        ),
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )
    return fig

def _radar_layout(fig, rmax):
    fig.update_layout(
        template="apricot",
        showlegend=True, legend_title_text="University",
        legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.25, yanchor='top'),
        margin=dict(l=40,r=40,t=10,b=140),
        polar=dict(
            angularaxis=dict(categoryorder="array", categoryarray=LABELS_FULL,
                             gridcolor="#e9edf2", linecolor="#cfd6df"),
            radialaxis=dict(range=[0,rmax], gridcolor="#e9edf2",
                            linecolor="#cfd6df", ticks="outside", showline=True)
        ),
        autosize=True
    )
    fig.update_polars(
        radialaxis=dict(gridcolor="#e3e9ef", linecolor="#cfd6df"),
        angularaxis=dict(gridcolor="#e3e9ef")
    )

@app.callback(Output("radar","figure"), Input("uni1","value"), Input("uni2","value"))
def make_radar(u1, u2):
    def base(rmax=100):
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[0]*6, theta=LABELS_FULL, mode="lines"))
        _radar_layout(fig, rmax); return fig
    if not u1 or not u2: return base()

    r1 = df2.loc[df2["name"]==u1, METRIC_KEYS]
    r2 = df2.loc[df2["name"]==u2, METRIC_KEYS]
    if r1.empty or r2.empty: return base()

    r1, r2 = r1.iloc[0].astype(float).values, r2.iloc[0].astype(float).values
    rmax = 100 if np.nanmax([r1, r2]) <= 100 else float(np.ceil(np.nanmax([r1, r2])/10.0)*10.0)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=r1, theta=LABELS_FULL, name=u1, mode="lines+markers",
        line=dict(color=THEME["series_primary"], width=3),
        marker=dict(size=6, color=THEME["series_primary"]),
        fill="toself", fillcolor="rgba(47,125,209,0.25)"
    ))
    fig.add_trace(go.Scatterpolar(
        r=r2, theta=LABELS_FULL, name=u2, mode="lines+markers",
        line=dict(color=THEME["series_accent"], width=3),
        marker=dict(size=6, color=THEME["series_accent"]),
        fill="toself", fillcolor="rgba(228,87,86,0.25)"
    ))
    _radar_layout(fig, rmax)
    return fig

@app.callback(Output('ranking_chart','figure'),
              Input('university_dropdown','value'),
              Input('country_dropdown','value'))
def update_chart(selected_universities, selected_country):
    f = df3_long.copy()
    if selected_country: f = f[f["Country"]==selected_country]
    if isinstance(selected_universities, str): selected_universities=[selected_universities]
    if selected_universities: f = f[f["University"].isin(selected_universities)]

    fig = (
        px.line(
            f, x="Year", y="Rank",
            color="University",
            markers=True,
            hover_data=["Country","Region"],
            color_discrete_sequence=THEME["categorical"],
            template="apricot"
        ) if not f.empty else px.line(title="No data available for selected filters", template="apricot")
    )

    fig.update_xaxes(type='category', automargin=True)
    if not f.empty:
        fig.update_yaxes(autorange="reversed", automargin=True)
    else:
        fig.update_yaxes(automargin=True)

    fig.update_layout(
        title="University Ranking Trends (2023–2026)",
        xaxis_title="Year", yaxis_title="Rank (Lower is Better)",
        legend=dict(
            orientation='h',
            x=0.5, xanchor='center',
            y=-0.22, yanchor='top'
        ),
        margin=dict(l=40, r=30, t=70, b=160),
        paper_bgcolor="white", plot_bgcolor="white"
    )

    return fig

@app.callback([Output('top10_table','data'), Output('top10_table','columns'),
               Output('region_table','data'), Output('region_table','columns')],
              [Input('year_radio','value'), Input('region_dropdown','value')])
def update_tables(selected_year, selected_region):
    top10 = df3.sort_values(by=selected_year).head(10)[["University","Country",selected_year]]
    region_df = df3 if not selected_region else df3[df3["Region"]==selected_region]
    region_df = region_df.sort_values(by=selected_year)[["University","Country",selected_year]]
    cols = lambda d: [{"name":c, "id":c} for c in d.columns]
    return (top10.to_dict('records'), cols(top10), region_df.to_dict('records'), cols(region_df))

if __name__ == "__main__":
    app.run(debug=True)
