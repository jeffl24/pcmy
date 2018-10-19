import os
import numpy as np
import pandas as pd
from glob import glob
pd.options.display.max_columns = 999

folder_location = glob('C:\\Users\limzi\OneDrive\Forecasting & Reporting\Jeff Files\PowerBi Files\pcsg_shopify\*.csv')

pcsg_shopify = pd.concat([pd.read_csv(x, parse_dates=['Paid at', 'Created at'], date_parser=lambda x: pd.to_datetime(x.rpartition('+')[0]), dtype={'Lineitem sku': 'str', 'Name': 'str'}) for x in folder_location] ,ignore_index=True)

# len(pcsg_shopify)
# pcsg_shopify.drop_duplicates(inplace = True)
# pcsg_shopify.drop_duplicates(inplace = True)
# len(pcsg_shopify)

keep_columns = ['Name', 'Email','Paid at', 'Subtotal', 'Shipping', 'Taxes', 'Total', 'Discount Code', 'Discount Amount','Created at', 'Lineitem quantity', 'Lineitem name', 'Lineitem price', 'Lineitem compare at price', 'Lineitem sku','Lineitem discount']

pcsg_shopify_simple = pcsg_shopify[keep_columns].sort_values('Name', ascending = False).drop_duplicates()

# len(pcsg_shopify_simple)

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
pcsg_shopify_simple = pd.merge(pcsg_shopify_simple, bundle_master, left_on="Lineitem sku", right_on = 'parent_sku', how='left')

pcsg_shopify_simple['parent_sku'].fillna(pcsg_shopify_simple['Lineitem sku'], inplace=True)
pcsg_shopify_simple['child_sku'].fillna(pcsg_shopify_simple['Lineitem sku'], inplace=True)


# pcsg_shopify_merge['total_quantity'].fillna(pcsg_shopify_merge['Lineitem quantity'], inplace = True)

# Calculates the actual quantity of composite SKUs sold (since, e.g., there might be more than one 2010s sold in a bundle)
pcsg_shopify_simple['child_subtotal_quantity'] =  pcsg_shopify_simple['child_quantity'] * pcsg_shopify_simple['Lineitem quantity']
# same concept, repeat the quantities with individual SKUs in the child_quantity column
pcsg_shopify_simple['child_subtotal_quantity'].fillna(pcsg_shopify_simple['Lineitem quantity'], inplace=True)

pcsg_shopify_simple['bundle_status'] = pcsg_shopify_simple['parent_name'].apply(lambda x: 0 if pd.isna(x) else 1)

#
def replace_bundle_products(x):
    '''
    This function corrects the values at column 'lineitem compare at price' to indicate the
    individual non-discounted price of the SKU
    '''
    if (x['Lineitem compare at price'] == 0 or np.isnan(x['Lineitem compare at price'])):
        # return x['Lineitem price']
        if np.isnan(x['Price']):
            return x['Lineitem price']
        else:
            return x['Price']
    else:
        return x['Lineitem compare at price']
pcsg_shopify_simple['Lineitem compare at price'] = pcsg_shopify_simple.apply(replace_bundle_products, axis = 1)

# Corrects the "Lineitem price" column
pcsg_shopify_simple['Lineitem price'] = pcsg_shopify_simple.apply(lambda x: x['Lineitem price'] if np.isnan(x['Discount Unit Price']) else x['Discount Unit Price'], axis = 1)

# keep_merge_columns = ['Name', 'Email', 'Paid at', 'Subtotal', 'Shipping', 'Taxes', 'Total', 'Discount Code', 'Discount Amount', 'Created at', 'Lineitem quantity', 'Lineitem name', 'Lineitem price', 'Lineitem compare at price', 'Lineitem sku', 'Lineitem discount', 'parent_sku', 'parent_name', 'child_sku', 'child_name', 'child_quantity',  'child_subtotal_quantity', 'bundle_status']

pcsg_shopify_simple.to_csv('C:\\Users\limzi\OneDrive\Forecasting & Reporting\Jeff Files\PowerBi Files\pcsg_shopify_debundled\pcsg_shopify_orders_debundled.csv')
