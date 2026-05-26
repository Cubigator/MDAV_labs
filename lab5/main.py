from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from lab5.functions import get_period_stats, get_seasons, get_players_data, get_penalty_data

ICE_BLUE = "#E1F0FF"
DEEP_BLUE = "#0A2C52"
RED_ACCENT = "#C8102E"
SILVER = "#808080"
WHITE = "#FFFFFF"
DARK = "#1A1A1A"

game_data = pd.read_csv('archive/game.csv')
game_plays_data = pd.read_csv('archive/game_plays.csv')
game_plays_players_data = pd.read_csv('archive/game_plays_players.csv')
players_info_data = pd.read_csv('archive/player_info.csv')
game_skater_stats_data = pd.read_csv('archive/game_skater_stats.csv')

seasons = get_seasons(game_data)

shots_data = game_plays_data[(game_plays_data['event'].isin(['Shot', 'Goal'])) & (game_plays_data['period'] <= 3)]

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

kpi_data = [
    {
        "value": "67.9%",
        "title": "Побед у команды, забившей первой",
        "description": "Гол открытия счёта даёт решающее преимущество",
        "color": DEEP_BLUE,
        "icon": "🥇"
    },
    {
        "value": "+20.9%",
        "title": "Преимущество домашней площадки",
        "description": "Родные трибуны добавляют пятую часть к шансам",
        "color": DARK,
        "icon": "🏟️"
    },
    {
        "value": "10.7%",
        "title": "Шанс на камбэк после 2-го периода",
        "description": "Только каждая десятая команда переворачивает игру в третьем",
        "color": RED_ACCENT,
        "icon": "🔄"
    },
]

season_dropdown = html.Div([
    html.Label(
        "Выберите сезон:",
        style={
            "fontWeight": "600",
            "color": "#0A2C52",
            "fontSize": "0.9rem",
            "marginBottom": "8px",
        }
    ),
    dcc.Dropdown(
        id='season-dropdown',
        options=seasons,
        value='Все сезоны', # значение по умлочанию
        searchable=False,
        style={
            "borderRadius": "6px",
            "border": "1px solid #D1E3F5"
        }
    )
], style={"padding": "8px 20px 18px 20px"})

kpi_cards = dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            # Верхняя плашка с процентом
                            html.Div(
                                [
                                    html.Span(kpi["icon"], style={"fontSize": "1.8rem", "marginRight": "8px"}),
                                    html.Span(
                                        kpi["value"],
                                        style={
                                            "fontSize": "2.4rem",
                                            "fontWeight": "800",
                                            "color": WHITE,
                                            "letterSpacing": "1px",
                                        },
                                    ),
                                ],
                                style={
                                    "backgroundColor": kpi["color"],
                                    "padding": "18px 20px",
                                    "borderRadius": "8px 8px 0 0",
                                    "display": "flex",
                                    "alignItems": "center",
                                },
                            ),
                            html.Div(
                                [
                                    html.H5(
                                        kpi["title"],
                                        className="fw-bold mt-2 mb-1",
                                        style={"color": DARK, "fontSize": "0.95rem", "lineHeight": "1.3"},
                                    ),
                                    html.Hr(style={"margin": "6px 0"}),
                                    html.P(
                                        kpi["description"],
                                        className="small mb-0",
                                        style={"color": SILVER, "fontSize": "0.8rem", "fontStyle": "italic"},
                                    ),
                                ],
                                style={"padding": "8px 20px 18px 20px"},
                            ),
                        ],
                        style={"padding": "0"},
                    )
                ],
                style={
                    "border": f"1px solid {ICE_BLUE}",
                    "borderRadius": "10px",
                    "boxShadow": "0 4px 12px rgba(0, 20, 40, 0.08)",
                    "transition": "transform 0.2s, box-shadow 0.2s",
                    "cursor": "default",
                },
                className="h-100",
            ),
            width=4,
        )
        for kpi in kpi_data
    ],
    className="g-3 mb-4",
)

app.layout = dbc.Container(
    fluid=True,
    children=[
        html.H1(
            "🏒 Анатомия матча НХЛ: закономерности и мифы",
            className="display-4 fw-bold text-center",
            style={
                "color": DARK,
                "fontSize": "2.5rem",
                "padding": "0px 0px 10px 0px",
            }
        ),
        season_dropdown,
        kpi_cards,
        dcc.Graph(figure={}, id='shots-periods-graphic'),
        dcc.Graph(figure={}, id='forwards-vs-defendsman-graphic'),
        dcc.Graph(figure={}, id='penalty-stats-graphic'),
    ],
    style={
        "padding": "24px 32px",
        "backgroundColor": ICE_BLUE
    }
)

@callback(
    Output('shots-periods-graphic', 'figure'),
    Input('season-dropdown', 'value')
)
def create_periods_chart(selected_season):
    period_stats = get_period_stats(game_data, game_plays_data, selected_season)

    fig = px.bar(period_stats, x='period', y='conversion_rate',
                 title=f'Реализация бросков по периодам ({selected_season})',
                 labels={'period': 'Период', 'conversion_rate': 'Реализация, %'},
                 text=period_stats['conversion_rate'].round(2))
    fig.update_traces(textposition='outside', marker_color='#4C72B0')
    fig.update_layout(yaxis_range=[0, 20], showlegend=False)

    return fig


@callback(
    Output('forwards-vs-defendsman-graphic', 'figure'),
    Input('season-dropdown', 'value')
)
def create_age_chart(selected_season):
    fwd_goals, def_goals = get_players_data(game_data,
                     game_plays_players_data,
                     game_plays_data,
                     players_info_data,
                     selected_season)
    fig = go.Figure()
    f = fwd_goals[(fwd_goals['age'] >= 18) & (fwd_goals['age'] <= 40)]
    d = def_goals[(def_goals['age'] >= 18) & (def_goals['age'] <= 40)]

    fig.add_trace(go.Scatter(x=f['age'], y=f['pct'], mode='lines+markers',
                             name='Нападающие', line=dict(color='#4C72B0', width=2)))
    fig.add_trace(go.Scatter(x=d['age'], y=d['pct'], mode='lines+markers',
                             name='Защитники', line=dict(color='#C44E52', width=2)))

    fig.add_vline(x=27, line_dash='dash', line_color='blue', opacity=0.3)
    fig.add_vline(x=29, line_dash='dash', line_color='red', opacity=0.3)

    fig.update_layout(
        title=f'Пик результативности: нападающие vs защитники ({selected_season})',
        xaxis_title='Возраст', yaxis_title='Голы (% от максимума)',
        template='plotly_white', hovermode='x unified'
    )
    return fig

@callback(
    Output('penalty-stats-graphic', 'figure'),
    Input('season-dropdown', 'value')
)
def create_discipline_chart(selected_season):

    means = get_penalty_data(game_data,
                     game_plays_data,
                     game_plays_players_data,
                     game_skater_stats_data,
                     selected_season)
    fig = px.bar(means, x='group', y='penalty_count',
                 title=f'Среднее количество удалений за матч ({selected_season})',
                 labels={'group': '', 'penalty_count': 'Удалений за матч'},
                 text=means['penalty_count'].round(4),
                 color='group',
                 color_discrete_map={'Топ-3 (лидеры)': '#4C72B0', '3-4 звено': '#C44E52'})
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False)

    return fig

if __name__ == '__main__':
    app.run(debug=True)