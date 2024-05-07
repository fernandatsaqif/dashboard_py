import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings("ignore")

# Set Page Config
st.set_page_config(
    page_title="Dashboard - Coffee Sales",
    page_icon="📊",
    layout="wide",
)

# Set Dashboard Title
st.title("Coffee Sales Dashboard 🍵")
st.markdown('<style>div.block-container{padding-top:1rem}</style>',unsafe_allow_html=True)

# Upload dan Baca data
fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename)
else:
    os.chdir(r"E:\py_visdat")
    df = pd.read_csv("coffee_sales.csv", encoding = "ISO-8859-1")  

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

#Atur Min dan max date
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date",startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date",endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

#membuat sidebar
st.sidebar.header("Choose your filter: ")


#Create filter for Cust. Country
country = st.sidebar.multiselect("Pick your country",df["Customer Country"].unique())
if not country:
    df2 = df.copy()
else:
    df2 = df[df["Customer Country"].isin(country)]

#Create filter for Roast Type
roast = st.sidebar.multiselect("Pick your Roast type",df2["Product Roast Type"].unique())
if not roast:
    df3 = df2.copy()
else:
    df3 = df2[df2["Product Roast Type"].isin(roast)]

#Create filter for Product Size (kg)
size = st.sidebar.multiselect("Pick your Product Size",df3["Product Size (kg)"].unique())

st.sidebar.header("09040622059 - Fernanda Widyadhana Tsaqif")

#Filter berdasarkan country, roast, dan size
if not country and not roast and not size:
    filtere_df = df
elif not roast and not size:
    filtere_df = df[df["Customer Country"].isin(country)]
elif not country and not size:
    filtere_df = df[df["Product Roast Type"].isin(roast)]
elif roast and size:
    filtere_df = df3[df["Product Roast Type"].isin(roast) & df3["Product Size (kg)"].isin(size)] 
elif country and size:
    filtere_df = df3[df["Customer Country"].isin(country) & df3["Product Size (kg)"].isin(size)] 
elif country and roast:
    filtere_df = df3[df["Customer Country"].isin(country) & df3["Product Roast Type"].isin(roast)] 
elif roast:
    filtere_df = df3[df3["Product Roast Type"].isin(roast)] 
else:
    filtere_df = df3[df3["Customer Country"].isin(country) & df3["Product Roast Type"].isin(roast)] & df3[df3["Product Size (kg)"].isin(size)]

category_df = filtere_df.groupby(by = ["Product Coffee Type"], as_index = False)["Order Quantity"].sum()


#Grafik Penjualan Produk Kopi Tertinggi
with col1:
    st.subheader("Penjualan Produk Kopi Tertinggi")
    fig = px.bar(category_df, x = "Product Coffee Type", y = "Order Quantity", text = ['${:,.2f}'.format(x) for x in category_df["Order Quantity"]], template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

#Grafik Penjualan berdasarkan wilayah
with col2:
    st.subheader("Penjualan berdasarkan wilayah")
    fig = px.pie(filtere_df, values = "Order Quantity", names = "Customer Country", hole = 0.5)
    fig.update_traces(text = filtere_df["Customer Country"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns((2))

#Download data Penjualan Produk Kopi Tertinggi
with cl1:
    with st.expander("ViewData : Product Coffee Type"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "ProductCoffee.csv", mime = "text/csv",
                               help = 'Click here to download the data as a CSV File')
        
#Download data Penjualan berdasarkan wilayah        
with cl2:
    with st.expander("ViewData : Customer Country"):
        custcountry = filtere_df.groupby(by = ["Customer Country"], as_index = False)["Order Quantity"].sum()
        st.write(custcountry.style.background_gradient(cmap="Oranges"))
        csv = custcountry.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Custcountry.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV File')
        
#Grafik data pemesanan berdasarkan waktu
filtere_df["month_year"] = filtere_df["Order Date"].dt.to_period("M")
st.subheader('Data Pemesanan berdasarkan waktu')

linechart = pd.DataFrame(filtere_df.groupby(filtere_df["month_year"].dt.strftime("%Y : %b"))["Order Quantity"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Order Quantity", labels = {"Order Quantity": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

#Membuat tree map berdasarkan "Customer Country","Product Coffee Type","Product Roast Type","Order Quantity"
st.subheader("Tampilan hierarki Penjualan menggunakan TreeMap")
fig3 = px.treemap(filtere_df, path = ["Customer Country","Product Coffee Type","Product Roast Type"], values = "Order Quantity",hover_data = ["Order Quantity"],
                  color = "Product Roast Type")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)


