import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

st.set_page_config(page_title="Covid Dashboard", page_icon=":chart_with_upwards_trend:", layout="wide")
st.title(":chart_with_upwards_trend: Covid Dashboard")
covid_data = pd.read_csv('covid_19_clean_complete.csv')
covid_data.rename(columns={'Date': 'date', 'Country/Region': 'country', 'Confirmed': 'cases', 'Deaths': 'deaths', 'Recovered': 'recovered'}, inplace=True)

# Date picker
col1, col2 = st.columns(2)
covid_data['date'] = pd.to_datetime(covid_data['date'], format='%m/%d/%Y')

startDate = pd.to_datetime(covid_data['date']).min()
endDate = pd.to_datetime(covid_data['date']).max()
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

covid_data = covid_data[(covid_data['date'] >= date1) & (covid_data['date'] <= date2)].copy()

st.sidebar.header("Choose your filter:")
selected_region = st.sidebar.selectbox("Select WHO Region", covid_data['WHO Region'].unique())

if selected_region:
    countries_in_region = covid_data[covid_data['WHO Region'] == selected_region]['country'].unique()

    if countries_in_region.size > 0:
        selected_country_pie = st.sidebar.selectbox("Select Country for Pie Chart", countries_in_region)
        selected_country_bar = st.sidebar.selectbox("Select Country for Bar Chart", countries_in_region)
    else:
        selected_country_pie = None
        selected_country_bar = None
else:
    selected_country_pie = None
    selected_country_bar = None

if selected_region and selected_country_pie:
    filtered_data_pie = covid_data[(covid_data['WHO Region'] == selected_region) & (covid_data['country'] == selected_country_pie)]
else:
    filtered_data_pie = covid_data

if selected_region and selected_country_bar:
    filtered_data_bar = covid_data[(covid_data['WHO Region'] == selected_region) & (covid_data['country'] == selected_country_bar)]
else:
    filtered_data_bar = covid_data

filtered_data = covid_data

st.subheader("Covid-19 Statistics")

col1, padding, col2 = st.columns((12, 1, 12))

with col1:
    total_cases_pie = filtered_data_pie['cases'].sum()
    total_deaths_pie = filtered_data_pie['deaths'].sum()
    total_recoveries_pie = filtered_data_pie['recovered'].sum()

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <div style="width: 23%; background-color: #e6f7ff; padding: 10px; border-radius: 8px; text-align: center;">
                <h3 style="color: #005580;">Cases</h3>
                <p>{total_cases_pie}</p>
            </div>
            <div style="width: 23%; background-color: #ffb3b3; padding: 10px; border-radius: 8px; text-align: center;">
                <h3 style="color: #990000;">Deaths</h3>
                <p>{total_deaths_pie}</p>
            </div>
            <div style="width: 38%; background-color: #ccffcc; padding: 10px; border-radius: 8px; text-align: center;">
                <h3 style="color: #008000;">Recoveries</h3>
                <p>{total_recoveries_pie}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    pie_chart = px.pie(
        covid_data.melt(id_vars=['date'], value_vars=['cases', 'deaths', 'recovered']),
        names='variable',
        values='value',
        color='variable',
        color_discrete_map={'cases': '#4dd2ff', 'deaths': '#ff8080', 'recovered': '#4dffb8'},
    )

    pie_chart.update_layout(height=500, width=500)
    st.plotly_chart(pie_chart)
    st.download_button(
        label="Download Pie Chart Data (CSV)",
        data=covid_data.melt(id_vars=['date'], value_vars=['cases', 'deaths', 'recovered']).to_csv(index=False, encoding='utf-8'),
        file_name='pie_chart_data.csv',
        key='download_pie_data',
        help="Download data for Pie Chart",
    )

with col2:
    bar_chart_data = covid_data.melt(id_vars=['date'], value_vars=['cases', 'deaths', 'recovered'], var_name='Metric', value_name='Count')

    total_cases_bar = filtered_data_bar['cases'].sum()
    total_deaths_bar = filtered_data_bar['deaths'].sum()
    total_recoveries_bar = filtered_data_bar['recovered'].sum()

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; margin-bottom: 80px;">
            <div style="width: 23%; background-color: #e6f7ff; padding: 10px; border-radius: 8px; text-align: center;">
                <h3 style="color: #005580;">Cases</h3>
                <p>{total_cases_bar}</p>
            </div>
            <div style="width: 23%; background-color: #ffb3b3; padding: 10px; border-radius: 8px; text-align: center;">
                <h3 style="color: #990000;">Deaths</h3>
                <p>{total_deaths_bar}</p>
            </div>
            <div style="width: 38%; background-color: #ccffcc; padding: 10px; border-radius: 8px; text-align: center;">
                <h3 style="color: #008000;">Recoveries</h3>
                <p>{total_recoveries_bar}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    bar_chart = px.bar(
        bar_chart_data,
        x='Metric',
        y='Count',
        title='Covid-19 Data',
        labels={'Count': 'Count', 'Metric': 'Metric'},
        color='Metric',
        color_discrete_map={'cases': '#4dd2ff', 'deaths': '#ff8080', 'recovered': '#4dffb8'},
    )

    bar_chart.update_layout(
        height=425,
        width=600,
        bargap=0.2,
        title_text='Covid-19 Data',
    )

    st.plotly_chart(bar_chart)
    bar_data_grouped = bar_chart_data.groupby(['Metric', 'date']).sum().reset_index()

    st.download_button(
        label="Download Bar Chart Data (CSV)",
        data=bar_data_grouped.to_csv(index=False, encoding='utf-8'),
        file_name='bar_chart_data.csv',
        key='download_bar_data',
        help="Download data for Bar Chart",
    )

with col1:
    st.subheader("Deaths all over the world")

    fig_deaths = px.choropleth(
        filtered_data,
        locations='country',
        locationmode='country names',
        color='deaths',
        color_continuous_scale='Reds',
        labels={'deaths': 'Deaths'},
    )
    fig_deaths.update_layout(height=500, width=500)
    st.plotly_chart(fig_deaths)

with col2:
    st.subheader("Recoveries all over the world")
    fig_recoveries = px.choropleth(
        filtered_data,
        locations='country',
        locationmode='country names',
        color='recovered',
        color_continuous_scale='greens',
        labels={'recoveries': 'Recoveries'},
    )
    fig_recoveries.update_layout(height=500, width=500)
    st.plotly_chart(fig_recoveries)


# Line chart
st.subheader("Line Chart - Covid-19 Cases Over Time")
line_chart = px.line(
    covid_data,
    x='date',
    y='cases',
    title='Covid-19 Cases Over Time',
    labels={'date': 'Date', 'cases': 'Cases'},
)
st.plotly_chart(line_chart)

# Time series plot
st.subheader("Time Series Plot - Covid-19 Deaths Over Time")
time_series_plot = px.scatter(
    covid_data,
    x='date',
    y='deaths',
    title='Covid-19 Deaths Over Time',
    labels={'date': 'Date', 'deaths': 'Deaths'},
)
st.plotly_chart(time_series_plot)
# Create the line chart
line_chart = px.line(
    bar_chart_data,  # Assuming bar_chart_data contains the necessary data
    x='date',        # Assuming 'date' is the x-axis variable
    y='Count',       # Assuming 'Count' is the y-axis variable
    title='Covid-19 Data',
    labels={'Count': 'Count', 'date': 'Date'},  # Update labels if needed
    color='Metric',  # Color lines based on 'Metric'
    color_discrete_map={'cases': '#4dd2ff', 'deaths': '#ff8080', 'recovered': '#4dffb8'},
)

# Update layout parameters
line_chart.update_layout(
    height=425,
    width=600,
    title_text='Covid-19 Data',
)

# Show the line chart
st.plotly_chart(line_chart)
