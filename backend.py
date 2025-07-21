import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

def load_local_data(filename = 'dirty_cafe_sales.csv'):
    """
    Loads local data from a CSV file.
    Converts common NaN values to a general NaN value.
    Changes data types of specific columns.
    """
    df = pd.read_csv(filename)

    df = df.replace(['UNKNOWN', 'ERROR', ' '], np.nan)

    for col in df.columns:
        try:
            df[col] = df[col].astype(float)
        except:
            pass

    return df 

def numerical_na_fill(df):
    """
    Fills NaN values in a numerical column with the mean of that column.
    """
    #Numerical columns NA values filling
    items = [i for i in df['Item'].unique() if i not in (' ',np.nan)]
    price_per_item = {item : df[df['Item'] == item]['Price Per Unit'].unique()[0]
                    for item in items}
    item_per_price = {v : k for k, v in price_per_item.items()}

    for i in range(2):
        df.loc[df['Total Spent'].isna(),'Total Spent'] = df['Quantity'] * df['Price Per Unit']
        df.loc[df['Quantity'].isna(), 'Quantity'] = df['Total Spent']/df['Price Per Unit']
        df.loc[df['Price Per Unit'].isna(), 'Price Per Unit'] =  df['Total Spent']/df['Quantity']
        df.loc[df['Price Per Unit'].isna(), 'Price Per Unit'] = df['Item'].map(price_per_item)
        df.loc[df['Item'].isna(), 'Item'] = df['Price Per Unit'].map(item_per_price)

    #Drop rows with NaN values in the already filled columns
    df = df.dropna(subset=['Total Spent', 'Quantity', 'Price Per Unit', 'Item'])


    return df

def categorical_na_fill(df):
    """
    Fills NaN values in categorical columns with the mode of that column.
    """

    #Categorical columns fill NA, and new features added
    df['Payment Method'] = df['Payment Method'].fillna('Mixed')
    df['Location'] = df['Location'].fillna('Unknown')

    
    return df

def time_to_text(df):
    """
    Split time colums into day of week, month and year.
    """
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], errors='coerce')
    df['Day of Week'] = df['Transaction Date'].dt.day_name()
    df['Month'] = df['Transaction Date'].dt.month_name()
    df['Year'] = df['Transaction Date'].dt.year
    df = df.dropna(subset=['Transaction Date'])
    df = df.drop(columns=['Transaction Date'])
    
    return df


def daily_grouper(df, item, total, variable):


    grouped_item = df.loc[df['Item'].isin(item), ['Item', 'Day of Week', variable, 'Month', 'Year']].copy()

    grouped_item = grouped_item.groupby(['Item', 'Day of Week'])[variable].mean().round(2).reset_index()
    
    grouped_item.columns = ['Item', 'Day of Week', variable + ' Mean']
    
    categories_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    grouped_item['Day of Week'] = pd.Categorical(grouped_item['Day of Week'],
                                              categories = categories_days,
                                              ordered = True) 
    grouped_item = grouped_item.sort_values('Day of Week')

    

    if total:
        grouped_item = grouped_item.groupby('Day of Week', observed = False)[variable + ' Mean'].sum().round(2).reset_index()
        
        grouped_item['Item'] = 'Total'
    
    return grouped_item


def monthly_grouper(df, item, total, variable, season : bool = False):
    """
    Function to create monthly graphs.
    This is a placeholder for the actual implementation.
    """
    # Placeholder implementation
    grouped_item = df.loc[df['Item'].isin(item), ['Item', 'Month', variable, 'Day of Week', 'Year']].copy()

    categories_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    grouped_item['Month'] = pd.Categorical(grouped_item['Month'],
                                              categories = categories_months,
                                              ordered = True)

    grouped_item = grouped_item.groupby(['Item','Month','Year'], observed = False)[variable].sum().reset_index()

    if season:
        grouped_item['Month'] = grouped_item['Month'].astype(str)
        grouped_item['Month'] = grouped_item['Month'].replace(['January', 'February', 'March'], 'Spring')\
                .replace(['April', 'May', 'June'], 'Summer')\
                .replace(['July', 'August', 'September'], 'Autumn')\
                .replace(['October', 'November', 'December'], 'Winter')
        
        grouped_item = grouped_item.groupby(['Item', 'Month', 'Year'])[variable].sum().reset_index()

    grouped_item = grouped_item.groupby(['Item', 'Month'], observed = False)[variable].mean().round(2).reset_index()

    grouped_item.columns = ['Item', 'Month', variable + ' Mean']

    grouped_item = grouped_item.sort_values(by='Month')

    if total:
        grouped_item = grouped_item.groupby('Month', observed = False)[variable + ' Mean'].sum().round(2).reset_index()
        grouped_item['Item'] = 'Total'



    return grouped_item


def bar_line_graphs(df, kind, variable, total, time_hierarchy):

    
    base = alt.Chart(df).encode(
        x=time_hierarchy,
        y=alt.Y(variable + ' Mean', scale=alt.Scale(zero=False))
        ).properties(
            width=800,
            height=500
        )

    if total:
        
        if kind == 'Line':
            chart = base.mark_line()  
        elif kind == 'Bar':
            chart = base.mark_bar()

        return chart

    if kind == 'Line':
        
        line = base.mark_line().encode(
            color='Item'
        )   

        chart = line
        

    elif kind == 'Bar':

        bar = base.mark_bar().encode(
                color='Item',
        )

        chart = bar 

    return chart

    
def preffered_payment_and_location_method(df):

    method_preffered = df[['Transaction ID','Total Spent', 'Payment Method', 'Location']].copy()

    method_preffered = method_preffered.dropna()

    method_preffered['Total Spent'] = pd.cut(method_preffered['Total Spent'], 
                                            3,
                                            labels=['Low', 'Medium', 'High'])
    
    method_preffered = pd.pivot_table(method_preffered,
                                      index='Payment Method',
                                      values='Transaction ID',
                                      columns='Total Spent',
                                      aggfunc='count',
                                      margins=True,
                                      observed=False)
    
    return method_preffered.style.background_gradient(cmap='Blues')

