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
    
    # Heading
    dbc.Row([
        dbc.Col(html.H1("Healthcare Dashboard"), width=15, className='text-center my-5')
    ]),

    # Overview summary data
    dbc.Row([
        dbc.Col(html.Div(f"Total Patient Records: {num_records}"), width=5, className='text-center my-3 top-text'),
        dbc.Col(html.Div(f"Average Billing Amount: {avg_billing:,.2f}"), width=5, className='text-center my-3 top-text')
    ], className='mb-5'), #styling div (margin bottom = mb)

    # Patient (F/M) Demographics
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f'Patient Demographics', className='card-title'),
                    dcc.Dropdown(
                        id="gender-filter",
                        options=[{"label":gender, "value": gender} for gender in data['Gender'].unique()],
                        value=None, #automatically display None
                        placeholder="Select a Gender"
                    ),
                    dcc.Graph(id="age-distribution")
                ])
            ])
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f'Medical Condition Distribution', className='card-title'),
                    dcc.Graph(id="condition-distribution")
                ])
            ])
        ], width=6)
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
                    dcc.Slider(
                        id='billing-slider',
                        min=data['Billing Amount'].min(), #ranging from min value
                        max=data['Billing Amount'].max(), #up to max value
                        value=data['Billing Amount'].median(), #display starting value at the median/middle amount
                        marks={int(value): f"${int(value):,}" for value in data['Billing Amount'].quantile([
                            0,0.25, 0.5, 0.75, 1]).values},  #range
                        step=100 #up to 100$
                               
                    ),
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
                    dcc.RadioItems(
                        id='chart-type',
                        options=[{'label': 'Line Chart', 'value': 'line'}, {'label': 'Bar Chart', 'value': 'bar'}],
                        value='line',
                        inline=True,
                        className='mb-4'
                    ),
                    dcc.Dropdown(id='condition-filter',
                                 options=[{"label": condition, 'value': condition} for condition in data['Medical Condition'].unique()],
                                 value=None,
                                 placeholder="Select a Condition"),
                                 
                    dcc.Graph(id='admission-trends')
                ])
            ])
        ], width=12)
    ])

], fluid=True) 

####### Create callbacks (how information are pass around and display on the graph)

#age distribution based on gender roles
@app.callback(
    Output('age-distribution', 'figure'),
    Input('gender-filter', 'value')
)
def update_distribution(selected_gender):
    # returns selected gender if there is one else, returns the rest of the data
    if selected_gender:
        filtered_df = data[data['Gender'] == selected_gender]
    else:
        filtered_df = data
    
    if filtered_df.empty:
        return {}  #returns nothing as in dictionary

    # specify the figure type - histogram
    fig = px.histogram(
        filtered_df,
        x="Age",
        nbins=10,
        color="Gender",
        title="Age Distribution by Gender",
        color_discrete_sequence=['blue', 'red']
    )
    return fig


# medical condition distribution
@app.callback(
    Output("condition-distribution", 'figure'),
    Input("gender-filter", 'value')
)
def update_medical_condition(selected_gender):
    filtered_df = data[data['Gender'] == selected_gender] if selected_gender else data
    fig = px.pie(
        filtered_df,
        names='Medical Condition',
        title='Medical Condition Distribution Pie Chart'
    )
    return fig

# insurance provider comparison
@app.callback(
    Output('insurance-comparison', 'figure'),
    Input('gender-filter', 'value')
)
def update_insurance(selected_gender):
    filtered_df = data[data['Gender'] == selected_gender] if selected_gender else data
    fig = px.bar(
        filtered_df, x='Insurance Provider', y='Billing Amount', color='Medical Condition',
        barmode='group', #group all the medical condition
        title="Insurance Provider Price Comparison",
        color_discrete_sequence=px.colors.qualitative.Set2
    ) 
    return fig 

# billing distribution
@app.callback(
    Output('billing-distribution', 'figure'),
    [Input('gender-filter', 'value'),
     Input('billing-slider', 'value')]
)
def update_billing(selected_gender, slider_value):
    filtered_df = data[data['Gender'] == selected_gender] if selected_gender else data
    filtered_df = filtered_df[filtered_df['Billing Amount'] <= slider_value]

    fig = px.histogram(
        filtered_df,
        x='Billing Amount', nbins=10,
        title='Billing Amount Distribution'
    )
    return fig

# trends in admission
@app.callback(
    Output('admission-trends', 'figure'),
    [Input('chart-type', 'value'),
     Input('condition-filter', 'value')]
)
def update_admission(chart_type, selected_condition):
    filtered_df = data[data['Medical Condition'] == selected_condition] if selected_condition else data
    trend_df = filtered_df.groupby('Year Month').size().reset_index(name='Count')

    trend_df['Year Month'] = trend_df['Year Month'].astype(str)

    if chart_type == 'line':
        fig = px.line(
            trend_df,
            x='Year Month',
            y='Count',
            title='Admission Trends over time'
        )
    else:
        fig = px.bar(
            trend_df,
            x='Year Month',
            y='Count',
            title='Admission Trends'
        )

    return fig

if __name__ == '__main__':
    app.run(debug=True)