import pandas as pd
import numpy as np

def preprocess_data(data):
    data = data.copy()
    # Previously shown that InvoiceDate.1 is identical to InvoiceDate
    data = data.drop(['InvoiceDate.1'], axis=1)
    # Drop duplicates
    data.drop_duplicates(inplace=True)
    # Store data without duplicate in new variable for sanity check.
    data_without_duplicates = data.copy()

    # Make invoiceDate -> Datetime
    data['InvoiceDate'] = pd.to_datetime(data.InvoiceDate, cache=True)

    # Find Cancelled orders
    data['Cancelled']=np.where(data.InvoiceNo.apply(lambda l: l[0]=='C'), True, False)

    # Filter only sales
    data_sales = data.loc[(data.Cancelled==False)&((data.Quantity < 0) == False)].copy()
    data_sales.drop(['StockCode','Description','Quantity','CustomerID','Cancelled'], axis=1,inplace=True)

    # Create datetime columns
    data_sales['Year'] = data_sales.InvoiceDate.dt.year
    data_sales['Quarter'] = data_sales.InvoiceDate.dt.quarter
    data_sales['Month'] = data_sales.InvoiceDate.dt.month
    data_sales['Week'] = data_sales.InvoiceDate.dt.isocalendar().week
    data_sales['Weekday'] = data_sales.InvoiceDate.dt.weekday
    data_sales['Day'] = data_sales.InvoiceDate.dt.day
    data_sales['Dayofyear'] = data_sales.InvoiceDate.dt.dayofyear
    data_sales['Hour'] = data_sales.InvoiceDate.dt.hour
    data_sales['Date'] = pd.to_datetime(data_sales[['Year', 'Month', 'Day']])

    # December sales
    #dec2010_sales = data_sales.loc[data_sales['Date'] < pd.to_datetime('2010-12-10')]
    #dec2011_sales = data_sales.loc[data_sales['Date'] > pd.to_datetime('2011-11-30')]

    # December sales outcomes
    #y1 = dec2010_sales.groupby('Day').InvoiceNo.count()
    #y2 = dec2011_sales.groupby('Day').InvoiceNo.count()

    # Get date of first and last sale in data set
    first_sale_date = data_sales['Date'].min()
    last_sale_date = data_sales['Date'].max()

    # Define outcome as the number of invoices each date (day)
    n_sales_per_date = data_sales.groupby('Date').InvoiceNo.count()

    # As some days don't have any sales, those days would be missing in the "number of sales per date" series.
    # Add these missing days with a value 0.
    n_sales_per_date_filled_missing = n_sales_per_date.reindex(
        pd.date_range(first_sale_date, last_sale_date), fill_value=0)

    # Split into train/val and test data.
    # Train/validation data is data up to and including last day of november 2011
    train_and_validation_data = n_sales_per_date_filled_missing[n_sales_per_date_filled_missing.index < pd.to_datetime('2011-12-01')]
    test_data = n_sales_per_date_filled_missing[n_sales_per_date_filled_missing.index > pd.to_datetime('2011-11-30')]


    return data, data_without_duplicates, train_and_validation_data, test_data