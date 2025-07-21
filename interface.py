import streamlit as st
from streamlit import session_state as state
from backend import *
from predictions import model_training, predict_new_values

st.set_page_config(page_title="Business Analysis", layout="wide")


sales = load_local_data()
sales = numerical_na_fill(sales)
#sales = categorical_na_fill(sales)
sales = time_to_text(sales)


st.title("Business Analysis")
    
st.subheader("This app provides insights into cafe sales data, including daily trends and item performance.",
             divider = 'gray')

daily, monthly, method, prediction = st.tabs(['Daily Sales Analysis',
                                  'Monthly Sales Analysis',
                                  'Preferred Payment and Location Methods',
                                  'Sales Prediction'])

########## Daily Sales Analysis ##########

with daily:

    st.header("Daily Sales Analysis")

    col1_d, col2_d, col3_d, col4_d = st.columns([2,1,1,1])

    with col1_d:
        items_day = st.pills('Item', 
                options=sales['Item'].unique().tolist(),
                key='item_selection',
                selection_mode='multi',
                default = None)
        
    with col2_d:
        total_day = st.checkbox('Show Total', value=True, key='show_total')

    with col3_d:
        kind_day = st.selectbox('Graph Type', ['Bar', 'Line'],
                                key='graph_type_day')

    with col4_d:
        variable_day = st.selectbox('Variable', ['Total Spent', 'Quantity'],
                                    key='variable_day')


    item_per_day = daily_grouper(sales, sales['Item'].unique().tolist(), total_day, variable_day)
    chart_daily = bar_line_graphs(item_per_day, kind_day, variable_day, total_day, 'Day of Week')

    if 'chart_daily' not in st.session_state:
            state.chart_daily = chart_daily

    if 'df_daily' not in st.session_state:
        state.df_daily = item_per_day

    if items_day or kind_day or variable_day:
        if len(items_day) == len(sales['Item'].unique().tolist()) or len(items_day) == 0:
            state.total = True
        else:
            state.total = False

        item_per_day = daily_grouper(sales, items_day, total_day, variable_day)
        chart_daily = bar_line_graphs(item_per_day, kind_day, variable_day, total_day, 'Day of Week')
        state.chart_daily = chart_daily
        state.df_daily = item_per_day


    col1, col2 = st.columns([3, 1])  
        
    with col1:
        st.altair_chart(state.chart_daily, use_container_width=True)
        
    with col2:
        st.dataframe(state.df_daily[['Item', 'Day of Week', variable_day + ' Mean']].sort_values('Day of Week'),
                    hide_index=True)
        


############ Monthly Sales Analysis ##########

with monthly:

    st.header("Monthly Sales Analysis")

    col1_m, col2_m, col3_m, col4_m, col5_m = st.columns([2,1,1,1,1])

    with col1_m:
        items_month = st.pills('Item', 
                options=sales['Item'].unique().tolist(),
                key='item_selection_m',
                selection_mode='multi',
                default = None)
        
    with col2_m:
        season = st.checkbox('Seasonal Analysis', value=False, key='seasonal_analysis')

    with col3_m:
        total_month = st.checkbox('Show Total', value=True, key='show_total_m')

    with col4_m:
        kind_month = st.selectbox('Graph Type', ['Bar', 'Line'],
                                key='graph_type_month')

    with col5_m:
        variable_month = st.selectbox('Variable', ['Total Spent', 'Quantity'],
                                    key='variable_month')
        
    


    item_per_month = monthly_grouper(sales, sales['Item'].unique().tolist() , total_month, variable_month, season)
    chart_month = bar_line_graphs(item_per_month, kind_month, variable_month, total_month, 'Month')

    if 'chart_month' not in st.session_state:
            state.chart_month = chart_month

    if 'df_month' not in st.session_state:
        state.df_month = item_per_month

    if items_month or kind_month or variable_month:
        if len(items_month) == len(sales['Item'].unique().tolist()) or len(items_month) == 0:
            state.total = True
        else:
            state.total = False

        item_per_month = monthly_grouper(sales, items_month, total_month, variable_month, season)
        chart_month = bar_line_graphs(item_per_month, kind_month, variable_month, total_month, 'Month')
        state.chart_month = chart_month
        state.df_month = item_per_month

    col1_m, col2_m = st.columns([3, 1])  
        
    with col1_m:
        st.altair_chart(state.chart_month, use_container_width=True)
        
    with col2_m:
        st.dataframe(state.df_month[['Item', 'Month', variable_month + ' Mean']].sort_values('Month'),
                    hide_index=True)


############ Preffered payment and location methods ##########

with method:

    st.header("Preferred Payment and Location Methods")

    st.dataframe(preffered_payment_and_location_method(sales))


############ Preffered payment and location methods ##########

with prediction:

    prediction_variable = st.selectbox('Variable to Predict', ['Quantity', 'Total Spent'],
                                    key='prediction_variable')
    
    sales = categorical_na_fill(sales)

    model, mse, r2, encoder = model_training(sales, prediction_variable)

    n_test_values = 50
    test_values = pd.DataFrame({
        'Item' : np.random.choice(sales['Item'].unique(), n_test_values),
        'Day of Week' : np.random.choice(sales['Day of Week'].unique(), n_test_values),
        'Month' : np.random.choice(sales['Month'].unique(), n_test_values),
        'Year' : 2023*np.ones(n_test_values, dtype=int)
    }
    )

    predictions = predict_new_values(test_values, model, encoder, prediction_variable)

    if prediction_variable == 'Quantity':

        predicted_frame = daily_grouper(predictions, sales['Item'].unique().tolist(), False, 'Quantity')
        predicted_chart = bar_line_graphs(predicted_frame, 'Bar', 'Quantity', False, 'Day of Week')

    elif prediction_variable == 'Total Spent':

        predicted_frame = monthly_grouper(predictions, sales['Item'].unique().tolist(), True, 'Total Spent', False)
        predicted_chart = bar_line_graphs(predicted_frame, 'Line', 'Total Spent', True, 'Month')

    st.altair_chart(predicted_chart, use_container_width=True)
    st.dataframe(predictions, hide_index=True)
