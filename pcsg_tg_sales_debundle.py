import os
import numpy as np
import pandas as pd
from glob import glob
pd.options.display.max_columns = 999

folder_location = glob('C://Users/limzi/OneDrive/Forecasting & Reporting/Jeff Files/PowerBi Files/pcsg_tg_sales/*.csv')

pcsg_tg_sales = pd.concat([pd.read_csv(x,parse_dates=['Day'], dayfirst=True, dtype={'Variant SKU': 'str'}) for x in folder_location] ,ignore_index=True)

# pcsg_tg_sales.sort_values('Day', ascending = False)

sku_master = pd.read_excel("C:/Users/limzi/OneDrive/Forecasting & Reporting/PCSG Master List.xlsx", sheet_name='SKU List' )

# Import bundle sheet of masterlist file
bundle_master = pd.read_excel("C:/Users/limzi/OneDrive/Forecasting & Reporting/PCSG Master List.xlsx",
                              sheet_name='Bundles').rename(columns = {'Parent SKU': "parent_sku",
                                                                      'Parent Name': 'parent_name',
                                                                      'Quantity': 'child_quantity',
                                                                      'Child SKU': "child_sku",
                                                                      'Child Name': 'child_name'}).astype({'child_sku': 'str',
                                                                                                           'parent_sku': 'str'})
# Use (how = "Left") in order to duplicate the line item information on each composite SKU
pcsg_tg_sales = pd.merge(pcsg_tg_sales, bundle_master, left_on="Variant SKU", right_on = 'parent_sku', how='left')

pcsg_tg_sales['parent_sku'].fillna(pcsg_tg_sales['Variant SKU'], inplace=True)
pcsg_tg_sales['child_sku'].fillna(pcsg_tg_sales['Variant SKU'], inplace=True)


# pcsg_tg_sales_merge['total_quantity'].fillna(pcsg_tg_sales_merge['Lineitem quantity'], inplace = True)

# Calculates the actual quantity of composite SKUs sold (since, e.g., there might be more than one 2010s sold in a bundle)
pcsg_tg_sales['child_subtotal_quantity'] =  pcsg_tg_sales['child_quantity'] * pcsg_tg_sales['Quantity']
# same concept, repeat the quantities with individual SKUs in the child_quantity column
pcsg_tg_sales['child_subtotal_quantity'].fillna(pcsg_tg_sales['Quantity'], inplace=True)

pcsg_tg_sales['bundle_status'] = pcsg_tg_sales['parent_name'].apply(lambda x: 0 if pd.isna(x) else 1)

pcsg_tg_sales_sorted = pcsg_tg_sales.sort_values(['Day', 'Customer Name'], ascending = False)

keep_columns = ['Customer Name', 'Customer Type', 'Location Name', 'Shipping Country', 'Shipping State', 'Variant Name', 'Variant SKU', 'Day', 'Total Sales', 'Quantity', 'parent_sku', 'parent_name', 'child_sku', 'child_name', 'child_quantity', 'child_subtotal_quantity', 'bundle_status']

pcsg_tg_sales_sorted[keep_columns].to_csv("C:/Users/limzi/OneDrive/Forecasting & Reporting/Jeff Files/PowerBi Files/pcsg_tg_sales_debundled/tg_sales_debundled.csv")

# bundle = pcsg_tg_sales[(pcsg_tg_sales['bundle_status'] == 1) & (pcsg_tg_sales['child_sku'] == '2010')]
# bundle['child_subtotal_quantity'].sum()

# pcsg_tg_sales[(pcsg_tg_sales['child_sku'] == '2010')]['child_subtotal_quantity'].sum()
# Index(['Customer Name', 'Customer Type', 'Location Name', 'Shipping Country',
#        'Shipping State', 'Variant Name', 'Variant SKU', 'Day', 'Total Sales',
#        'Quantity', 'parent_sku', 'parent_name', 'child_sku', 'child_name',
#        'child_quantity', 'child_subtotal_quantity', 'bundle_status'],
#       dtype='object')
