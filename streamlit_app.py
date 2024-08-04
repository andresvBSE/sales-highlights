import streamlit as st
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", palette="pastel")

import matplotlib.pyplot as plt
from pathlib import Path

# Load the data
@st.cache
def load_data():
    DATA_FILENAME = Path(__file__).parent/'data/highlights.csv'
    df = pd.read_csv(DATA_FILENAME)
    
    df = df.query("Store<6") # only 5 stores
    df["Date"] = pd.to_datetime(df['Date'], format="%Y-%m-%d")
    df["Date S F"] = df['Date'].dt.strftime("%Y-%m-%d")
    df["Highlights"].fillna("", inplace=True)
    df.sort_values(by="Date", inplace=True)
    return df
data = load_data()

# Helper functions to calculate metrics
def get_total_sales(data, week):
    return data[data['Date S F'] == week]['Weekly_Sales'].sum()

def get_weekly_sales(data, week):
    return data[data['Date S F'] == week].groupby('Store')['Weekly_Sales'].sum()

def calculate_sales_variation(current_sales, last_sales):
    return ((current_sales - last_sales) / last_sales) * 100 if last_sales != 0 else 0

def get_weekly_highlights(data, week):
        return data[data['Date S F'] == week]["Highlights"].values[0]
    

# Get the list of available weeks
available_weeks = [week for week in data["Date S F"].unique()]#since the second week

# Streamlit app layout
st.title("Walmart Sales Dashboard")

# Week selector
selected_week = st.selectbox("Select Week", available_weeks, index=10) # by default present the week 10

# Calculate metrics for the selected week and the previous week

last_week_index = available_weeks.index(selected_week) - 1 if available_weeks.index(selected_week) - 1 >= 0 else 0
last_week =  available_weeks[last_week_index]

total_sales_current_week = get_total_sales(data, selected_week)
total_sales_last_week = get_total_sales(data, last_week)
sales_variation = calculate_sales_variation(total_sales_current_week, total_sales_last_week)

# Calculate store-wise sales for the bar chart
current_week_sales = get_weekly_sales(data, selected_week)
last_week_sales = get_weekly_sales(data, last_week)

# Main cards
st.subheader("Weekly Sales Summary")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Sales This Week", value=f"${total_sales_current_week:,.0f}")
with col2:
    st.metric(label="Total Sales Last Week", value=f"${total_sales_last_week:,.0f}")
with col3:
    st.metric(label="Sales Variation (%)", value=f"{sales_variation:.2f}%")

# Bar graph
st.subheader("Store-wise Weekly Sales Comparison")

# Prepare data for the bar plot
plot_data = pd.DataFrame({
    'Store': current_week_sales.index,
    'Current Week Sales': current_week_sales.values,
    'Last Week Sales': last_week_sales.values
}).melt(id_vars='Store', var_name='Week', value_name='Sales')

# Create a bar plot with Seaborn
plt.figure(figsize=(10, 6))
sns.barplot(data=plot_data, x='Store', y='Sales', hue='Week')
plt.title('Sales by Store and Week')
plt.xlabel('Store')
plt.ylabel('Sales')

st.pyplot(plt)

# Highlights ( this is the relevant part for this demo)
highlights_text = get_weekly_highlights(data, selected_week)
st.markdown(highlights_text)