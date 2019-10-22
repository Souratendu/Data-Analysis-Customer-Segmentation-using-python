#!/usr/bin/env python
# coding: utf-8

# In[2]:


from __future__ import division
from datetime import datetime, timedelta
import pandas as pd
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns



import chart_studio.plotly as py
import plotly.offline as pyoff
import plotly.graph_objs as go

#intiate visualization library for jupyter notebook
pyoff.init_notebook_mode()

tx_data = pd.read_csv('D:/Datasets/data.csv', encoding = "ISO-8859-1")

tx_data.head(10)


# In[ ]:





# In[3]:


tx_data.inf0()


# In[4]:


#Convert invoice date form string to date time
tx_data['InvoiceDate'] = pd.to_datetime(tx_data['InvoiceDate'])

#creating YearMonth field for the ease of reporting and visualization
tx_data['InvoiceYearMonth'] = tx_data['InvoiceDate'].map(lambda date: 100*date.year + date.month)

tx_data['Revenue'] = tx_data['Price'] * tx_data['Quantity']
tx_revenue = tx_data.groupby(['InvoiceYearMonth'])['Revenue'].sum().reset_index()
tx_revenue


# In[5]:


#X and Y axis inputs for Plotly graph. We use Scatter for line graphs
plot_data = [
    go.Scatter(
        x=tx_revenue['InvoiceYearMonth'],
        y=tx_revenue['Revenue'],
    )
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='Montly Revenue'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)


# In[6]:


#using pct_change() function to see monthly percentage change
tx_revenue['MonthlyGrowth'] = tx_revenue['Revenue'].pct_change()
#showing first 5 rows
tx_revenue.head(10)


# In[7]:


#visualization - line graph
plot_data = [
    go.Scatter(
        x=tx_revenue.query("InvoiceYearMonth < 201112")['InvoiceYearMonth'],
        y=tx_revenue.query("InvoiceYearMonth < 201112")['MonthlyGrowth'],
    )
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='Montly Growth Rate'
    )

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)


# In[23]:


tx_uk = tx_data.query("Country == 'United Kingdom'").reset_index(drop = True)
tx_monthly_active = tx_uk.groupby('InvoiceYearMonth')['Customer ID'].nunique().reset_index()
tx_monthly_active

plot_data =[
    go.Bar(
        x=tx_monthly_active['InvoiceYearMonth'],
        y=tx_monthly_active['Customer ID']
    )
    
]

plot_layout = go.Layout(
    xaxis={"type": "category"},
    title='Monthly Active Customer'
)

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)


# In[27]:



tx_monthly_sales = tx_uk.groupby('InvoiceYearMonth')['Quantity'].sum().reset_index()
tx_monthly_sales

plot_data =[
    go.Bar(
        x=tx_monthly_sales['InvoiceYearMonth'],
        y=tx_monthly_sales['Quantity']
    )
    
]

plot_layout = go.Layout(
    xaxis={"type": "category"},
    title='Monthly Total Quantity ordered'
)

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)


# In[30]:



tx_monthly_order_avg = tx_uk.groupby('InvoiceYearMonth')['Revenue'].mean().reset_index()
tx_monthly_order_avg

plot_data =[
    go.Bar(
        x=tx_monthly_order_avg['InvoiceYearMonth'],
        y=tx_monthly_order_avg['Revenue']
    )
    
]

plot_layout = go.Layout(
    xaxis={"type": "category"},
    title='Monthly Total Quantity ordered'
)

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)


# In[31]:


tx_min_purchase_date = tx_uk.groupby('Customer ID')['InvoiceDate'].min().reset_index()
tx_min_purchase_date.columns = ['Customer ID','MinPurchaseDate']
tx_min_purchase_date['MinPurchaseYearMonth'] = tx_min_purchase_date['MinPurchaseDate'].map(lambda date: 100*date.year + date.month)
tx_min_purchase_date

tx_uk = pd.merge(tx_uk,tx_min_purchase_date, on='Customer ID')
tx_uk.head()


# In[38]:




tx_uk['UserType'] = 'New'
tx_uk.loc[tx_uk['InvoiceYearMonth']>tx_uk['MinPurchaseYearMonth'],'UserType']= 'Existing'

tx_user_type_revenue = tx_uk.groupby(['InvoiceYearMonth','UserType'])['Revenue'].sum().reset_index()
tx_user_type_revenue = tx_user_type_revenue.query("InvoiceYearMonth != 201012 and InvoiceYearMonth != 201112")
plot_data = [
    go.Scatter(
        x = tx_user_type_revenue.query("UserType == 'Existing'")['InvoiceYearMonth'],
        y = tx_user_type_revenue.query("UserType == 'Existing'")['Revenue'],
        name = 'Existing'
    ),
    go.Scatter(
        x = tx_user_type_revenue.query("UserType == 'New'")['InvoiceYearMonth'],
        y = tx_user_type_revenue.query("UserType == 'New'")['Revenue'],
        name = 'New'
    )
]

plot_layout = go.Layout(
    xaxis={"type":"category"},
    title='New vs Existing'
)

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)


# In[41]:


#create a dataframe that shows new user ratio - we also need to drop NA values (first month new user ratio is 0)
tx_user_ratio = tx_uk.query("UserType == 'New'").groupby(['InvoiceYearMonth'])['Customer ID'].nunique()/tx_uk.query("UserType == 'Existing'").groupby(['InvoiceYearMonth'])['Customer ID'].nunique() 
tx_user_ratio = tx_user_ratio.reset_index()
tx_user_ratio = tx_user_ratio.dropna()

#print the dafaframe
tx_user_ratio

#plot the result

plot_data = [
    go.Bar(
        x=tx_user_ratio.query("InvoiceYearMonth>201101 and InvoiceYearMonth<201112")['InvoiceYearMonth'],
        y=tx_user_ratio.query("InvoiceYearMonth>201101 and InvoiceYearMonth<201112")['Customer ID'],
    )
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='New Customer Ratio'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)


# In[48]:


tx_user_purchase = tx_uk.groupby(['Customer ID','InvoiceYearMonth'])['Revenue'].sum().reset_index()

tx_user_purchase
tx_retention = pd.crosstab(tx_user_purchase['Customer ID'], tx_user_purchase['InvoiceYearMonth']).reset_index()

tx_retention.head()

#create an array of dictionary which keeps Retained & Total User count for each month
months = tx_retention.columns[2:]
retention_array = []
for i in range(len(months)-1):
    retention_data = {}
    selected_month = months[i+1]
    prev_month = months[i]
    retention_data['InvoiceYearMonth'] = int(selected_month)
    retention_data['TotalUserCount'] = tx_retention[selected_month].sum()
    retention_data['RetainedUserCount'] = tx_retention[(tx_retention[selected_month]>0) & (tx_retention[prev_month]>0)][selected_month].sum()
    retention_array.append(retention_data)
    
#convert the array to dataframe and calculate Retention Rate
tx_retention = pd.DataFrame(retention_array)
tx_retention['RetentionRate'] = tx_retention['RetainedUserCount']/tx_retention['TotalUserCount']

#plot the retention rate graph
plot_data = [
    go.Scatter(
        x=tx_retention.query("InvoiceYearMonth<201112")['InvoiceYearMonth'],
        y=tx_retention.query("InvoiceYearMonth<201112")['RetentionRate'],
        name="organic"
    )
    
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='Monthly Retention Rate'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)


# In[50]:


#create our retention table again with crosstab() - we need to change the column names for using them in .query() function
tx_retention = pd.crosstab(tx_user_purchase['Customer ID'], tx_user_purchase['InvoiceYearMonth']).reset_index()
new_column_names = [ 'm_' + str(column) for column in tx_retention.columns]
tx_retention.columns = new_column_names

#create the array of Retained users for each cohort monthly
retention_array = []
for i in range(len(months)):
    retention_data = {}
    selected_month = months[i]
    prev_months = months[:i]
    next_months = months[i+1:]
    for prev_month in prev_months:
        retention_data[prev_month] = np.nan
        
    total_user_count =  retention_data['TotalUserCount'] = tx_retention['m_' + str(selected_month)].sum()
    retention_data[selected_month] = 1 
    
    query = "{} > 0".format('m_' + str(selected_month))
    

    for next_month in next_months:
        query = query + " and {} > 0".format(str('m_' + str(next_month)))
        retention_data[next_month] = np.round(tx_retention.query(query)['m_' + str(next_month)].sum()/total_user_count,2)
    retention_array.append(retention_data)
    
tx_retention = pd.DataFrame(retention_array)
tx_retention.index = months

#showing new cohort based retention table
tx_retention

