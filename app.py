from configs import *

# Followed tutorial: https://www.youtube.com/watch?v=ArnxeE1NuMM
# load data and data featuring to clean data, returns the cleaned data
def load_data():
    df = pd.read_csv('assets/healthcare.csv')

    # data featuring - ensure data accuracy
    df['Billing Amount'] = pd.to_numeric(df['Billing Amount'], errors='coerce')
    df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])

    # create new column for Year month (date)
    df['Year Month'] = df['Date of Admission'].dt.to_period('M')
    return df

data = load_data()

# number of records within the dataset
num_records = len(data)

# avg billing per customer
avg_billing = data['Billing Amount'].mean()

# creating a webapp
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# app layout and design - per row, each row contains columns
app.layout = dbc.Container([ #starts with row, then column
    # row 1
    dbc.Row([
        dbc.Col(html.H1("Healthcare Dashboard"), width=15, className='text-center my-5')
    ]),

    # row 2
    dbc.Row([
        dbc.Col(html.Div(f"Total Patient Records: {num_records}"), width=7, className='text-center my-3 top-text'),
        dbc.Col(html.Div(f"Average Billing Amount: {avg_billing}"), width=7, className='text-center my-3 top-text')
    ], className='mb-5'), #styling div (margin bottom = mb)

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f'Patient Demographics', className='card-title'),
                    dcc.Dropdown(
                        id="gender-filter"
                    ),
                    dcc.Graph(id="age-distribution")
                ])
            ])
        ], width=7),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f'Medical Condition Distribution', className='card-title'),
                    dcc.Graph(id="condition-distribution")
                ])
            ])
        ], width=7)
    ]),

    # Insurance provider data
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f'Insurance Provider Comparison', className='card-title'),
                    dcc.Graph(id="insurance-comparison")
                ])
            ])
        ], width=12) #whole page
    ]),

    # Billing Distribution
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f'Billing Amount Distribution', className='card-title'),
                    dcc.Slider(id='billing-slider'),
                    dcc.Graph(id='billing-distribution')
                ])
            ])
        ], width=12)
    ]),

    # Trends in Admission
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f'Trends in Admission', className='card-title'),
                    dcc.RadioItems(id='chart-type'),
                    dcc.Dropdown(id='condition-filter'),
                    dcc.Graph(id='admission-trends')
                ])
            ])
        ], width=12)
    ])

], fluid=True) 





if __name__ == '__main__':
    app.run(debug=True)