from dash import Dash, dcc, html, Input, Output
import plotly.express as px

app = Dash(__name__)


app.title = "Análisis de accidentes"


################################################################
# Data manipulation
import pandas as pd
import os

# Load data
ruta_archivo = 'C:/Users/franc/OneDrive/Documentos/VScode/fco.ho/alan_proyect/data/tabla1.xlsx'

data = pd.read_excel(ruta_archivo)

# Figure 1: accidents by month
orden_deseado = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

data['MES'] = pd.Categorical(data['MES'], categories=orden_deseado, ordered=True)
accidentes_por_mes = data.groupby('MES').size().reset_index(name='cantidad')
accidentes_por_mes = accidentes_por_mes.sort_values('MES')

accidentes_por_supervisor = data.groupby('SUPERVISOR').size().reset_index(name='cantidad')
accidentes_por_supervisor.loc[accidentes_por_supervisor['cantidad'] < 4, 'SUPERVISOR'] = 'Others'
grouped_data = accidentes_por_supervisor.groupby('SUPERVISOR').sum().reset_index()

accidentes_por_parte = data.groupby('PARTE AFECTADA').size().reset_index(name='cantidad')
accidentes_por_parte = accidentes_por_parte.sort_values(by='cantidad', ascending=False)

# Define figures
fig2 = px.line(accidentes_por_mes, x="MES", y="cantidad", title='Accidentes por mes', width=800, height=600)
fig = px.pie(accidentes_por_supervisor, values='cantidad', names='SUPERVISOR', title='Accidentes por supervisor', width=800, height=600)
fig.update_traces(textinfo='none')

fig3 = px.histogram(accidentes_por_parte, x='PARTE AFECTADA', y='cantidad', title='Accidentes por parte afectada', width=800, height=600)


################################################################



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

@app.callback(
    Output('output-anio', 'children'),
    [Input('dropdown-anio', 'value')]
)
def actualizar_output(selected_year):
    return f'Has seleccionado el año {selected_year}'


app.run_server(debug=True)