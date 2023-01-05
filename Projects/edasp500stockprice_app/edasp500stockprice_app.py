import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yfinance as yf

st.title("S&P 500 Stock Price Explorer")

st.markdown(
    """
This app retrieves the list of the **S&P 500** (from Wikipedia) and its corresponding **stock closing price** (year-to-date)!
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, yfinance
* **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
"""
)

st.sidebar.header("User Input Features")

# Web scraping of S&P 500 data
#
@st.cache
def load_data():
    # Take the url, from where you want to scrap the data
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = pd.read_html(url, header=0)
    # first table = html[0]
    df = html[0]
    return df


# Create the DataFrame
df = load_data()

# Examining the Sectors
sectors_unique = df["GICS Sector"].unique()

# Aggregate the data
sector = df.groupby("GICS Sector")

# Sidebar - Sector selection
sorted_sector_unique = sorted(sectors_unique)

# Get the selected sector
selected_sector = st.sidebar.multiselect(
    "Sector", sorted_sector_unique, sorted_sector_unique
)

# Filtering data
df_selected_sector = df[(df["GICS Sector"].isin(selected_sector))]

st.header("Display Companies in the Selected Sector")
st.write(
    "Data Dimension: "
    + str(df_selected_sector.shape[0])
    + " rows and "
    + str(df_selected_sector.shape[1])
    + " columns."
)
st.dataframe(df_selected_sector)

# Download S&P500 data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="sp500.csv">Download CSV File</a>'
    return href


st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

# https://pypi.org/project/yfinance/
data = yf.download(  # or pdr.get_data_yahoo(...
    # tickers list or string as well
    tickers=list(df_selected_sector[:10].Symbol),
    # use "period" instead of start/end
    # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    # (optional, default is '1mo')
    period="ytd",
    # fetch data by interval (including intraday if period < 60 days)
    # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    # (optional, default is '1d')
    interval="1d",
    # group by ticker (to access via data['SPY'])
    # (optional, default is 'column')
    group_by="ticker",
    # adjust all OHLC automatically
    # (optional, default is False)
    auto_adjust=True,
    # download pre/post regular market hours data
    # (optional, default is False)
    prepost=True,
    # use threads for mass downloading? (True/False/Integer)
    # (optional, default is True)
    threads=True,
    # proxy URL scheme use use when downloading?
    # (optional, default is None)
    proxy=None,
)

st.set_option("deprecation.showPyplotGlobalUse", False)

# Plot Closing Price of Query Symbol
def price_plot(symbol):
    df = pd.DataFrame(data[symbol].Close)
    df["Date"] = df.index
    plt.fill_between(df.Date, df.Close, color="skyblue", alpha=0.3)
    plt.plot(df.Date, df.Close, color="skyblue", alpha=0.8)
    plt.xticks(rotation=90)
    plt.title(symbol, fontweight="bold")
    plt.xlabel("Date", fontweight="bold")
    plt.ylabel("Closing Price", fontweight="bold")
    return st.pyplot(plt)


num_company = st.sidebar.slider("Number of Companies", 1, 10)

if st.button("Show Plots"):
    st.header("Stock Closing Price")
    for i in list(df_selected_sector.Symbol)[:num_company]:
        price_plot(i)

## About
st.header("About")
st.write(
    """
Finish S&P Stock Price App
"""
)
