from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd

app = Dash(__name__)
server = app.server

app.title = "Análisis de accidentes"

# Cargar datos
accidentes_por_mes = pd.read_csv('accidentes_por_mes.csv')
accidentes_por_supervisor = pd.read_csv('accidentes_por_supervisor.csv')
accidentes_por_parte = pd.read_csv('accidentes_por_parte.csv')

fig = px.pie(accidentes_por_supervisor, values='cantidad', names='SUPERVISOR', title='Accidentes por supervisor', width=800, height=600)
fig.update_traces(textinfo='none')



fig2 = px.line(accidentes_por_mes, x="MES", y="cantidad", title='Accidentes por mes', width=600, height=600)

fig3 = px.histogram(accidentes_por_parte, x='PARTE AFECTADA', y='cantidad', title='Accidentes por parte afectada', width=800, height=600)

app.layout = html.Div(style={'backgroundColor': 'lightblue'}, children=[
    html.H1("Análisis de Accidentes", style={'textAlign': 'center'}),
    # Contenedor principal
    html.Div([
        # Gráfico principal
        html.Div([
            dcc.Graph(
                id='my-graph',
                figure=fig2
            )
        ], style={'width': '50%', 'float': 'left'}),  # Establecer ancho y alineación a la izquierda
        # Gráfico en la parte derecha
        html.Div([
            # Gráfico 1 en la parte superior
            html.Div([
                dcc.Graph(
                    id='graph1',
                    figure=fig
                )
            ]),
            # Gráfico 2 en la parte inferior
            html.Div([
                dcc.Graph(
                    id='graph2',
                    figure=fig3
                )
            ])
        ], style={'width': '50%', 'float': 'right'})  # Establecer ancho y alineación a la derecha
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False )
