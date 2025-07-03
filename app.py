import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os
from dash import Dash, html, dcc, Input, Output  # ✅ UPDATED IMPORTS

# external CSS stylesheets
external_stylesheets = [
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]


patients = pd.read_csv('IndividualDetails.csv')

total = patients.shape[0]
active = patients[patients['current_status']=='Hospitalized'].shape[0]
recovered = patients[patients['current_status']=='Recovered'].shape[0]
deaths = patients[patients['current_status']=='Deceased'].shape[0]

options = [
    {'label':'All','value':'All'},
    {'label':'Hospitalized','value':'Hospitalized'},
    {'label':'Recovered','value':'Recovered'},
    {'label':'Deceased','value':'Deceased'}
]


date_by_date = patients.groupby('diagnosed_date').size().reset_index(name='cases on that day')
date_by_date['diagnosed_date'] = pd.to_datetime(date_by_date['diagnosed_date'], dayfirst=True)
date_by_date = date_by_date.sort_values('diagnosed_date')

# Format as dd/mm/yy
date_by_date['diagnosed_date'] = date_by_date['diagnosed_date'].dt.strftime('%d/%m/%y')

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=date_by_date['diagnosed_date'],
    y=date_by_date['cases on that day'],
    mode='lines+markers',
    name='Daily Cases',
    line=dict(color='blue'),
    marker=dict(size=4)
))

fig.update_layout(
    title='COVID-19 Daily Cases Over Time',
    xaxis_title='Date',
    yaxis_title='Number of Cases',

    # ✅ Format X-axis tick labels as DD/MM/YY
    xaxis=dict(
        tickformat='%d/%m/%y',
        tickangle=45  # Optional: rotate for readability
    ),

    template='plotly_white'
)


df_age = pd.read_csv('AgeGroupDetails.csv')

fig_age = go.Figure(
    data=[go.Pie(
        labels=df_age['AgeGroup'],
        values=df_age['TotalCases'],
        textinfo='label+percent',
        hole=0.3,
        marker=dict(line=dict(color='#000000', width=1)),
        domain=dict(x=[0, 0.75]),  # ✅ Shift chart left only
        insidetextorientation='auto',
        showlegend=True  # ✅ Keeps legend as is
    )]
)

fig_age.update_layout(
    title='COVID-19 Age Group Distribution',
    template='plotly_white'
)




# ✅ Dash instance
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server  # ✅ Add this for Render


app.layout=html.Div([
    html.H1('COVID-19 Data Analysis',style={'color':'#000000','text-align':'center'}),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H3('Total Cases',className='text-light'),
                    html.H4(total,className='text-light')
                ],className='card-body'),
            ],className='card bg-danger')
        ],className='col-md-3'),
        html.Div([
            html.Div([
                html.Div([
                    html.H3('Active Cases',className='text-light'),
                    html.H4(active,className='text-light')
                ],className='card-body'),
            ],className='card bg-info')
        ],className='col-md-3'),
        html.Div([
            html.Div([
                html.Div([
                    html.H3('Recovered Cases',className='text-light'),
                    html.H4(recovered,className='text-light')
                ],className='card-body'),
            ],className='card bg-warning')
        ],className='col-md-3'),
        html.Div([
            html.Div([
                html.Div([
                    html.H3('Deaths',className='text-light'),
                    html.H4(deaths,className='text-light')
                ],className='card-body'),
            ],className='card bg-success')
        ],className='col-md-3')
    ],className='row mt-4'),

    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig)
                ],className='card-body'),
            ],className='card'),
        ],className='col-md-6'),

        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_age)
                ],className='card-body'),
            ],className='card'),
        ],className='col-md-6'),
    ],className='row mt-4'),

    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(id='picker',options=options,value='All'),
                    dcc.Graph(id='bar'),
                ],className='card-body'),
            ],className='card')
        ],className='col-md-12')
    ],className='row mt-4'),

],className='container')

@app.callback(Output('bar','figure'),[Input('picker','value')])
def update_graph(type):

    if type == 'All':

        pbar = patients['detected_state'].value_counts().reset_index()

        return {
            'data': [go.Bar(x=pbar['detected_state'] , y=pbar['count'])],
            'layout': go.Layout(title='State Total Count',)
        }
    else:

        npat = patients[patients['current_status'] == type]
        pbar = npat['detected_state'].value_counts().reset_index()

        return {
            'data': [go.Bar(x=pbar['detected_state'], y=pbar['count'])],
            'layout': go.Layout(title='State Total Count', )
        }


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))  # 8050 is fallback for local dev
    app.run(host="0.0.0.0", port=port, debug=True)




