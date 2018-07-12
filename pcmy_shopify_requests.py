
import requests
from requests.auth import HTTPBasicAuth
import json
import numpy as np
import pandas as pd
import pprint
import math
import datetime
pd.options.display.max_columns = 999

username = 'a8e0caf507870e4d91e140d75cb1e0c5'
password = '38b5c1a103fc779e956eab1436dc1934'

# Link to obtain basic info on PCMY store
url_shop_details = 'https://paulas-choice-malaysia.myshopify.com/admin/shop.json'

# obtain details of location_id for use in other queries
url_location_id = 'https://paulas-choice-malaysia.myshopify.com/admin/locations.json'
location_id_request = requests.get(url_location_id, auth=HTTPBasicAuth(username, password)).text
location_id_json = json.loads(location_id_request)
location_id = location_id_json['locations'][0]['id']

# Obtain the count of locations to multiply with the total number of SKUs
# in order to get the correct range() for looping through multiple pages
url_locations_count = 'https://paulas-choice-malaysia.myshopify.com/admin/locations/count.json'
locations_count_request = requests.get(url_locations_count, auth=HTTPBasicAuth(username, password)).text
locations_count_json = json.loads(locations_count_request)
locations_count = locations_count_json['count']
locations_count # = 1 since PCMY has only 1 location

url_products_count = 'https://paulas-choice-malaysia.myshopify.com/admin/products/count.json'
products_count_request = json.loads(requests.get(url_products_count,auth=HTTPBasicAuth(username, password)).text)
products_count = products_count_request['count']

url_products = 'https://paulas-choice-malaysia.myshopify.com/admin/products.json?limit=250'
products_request = requests.get(url_products, auth=HTTPBasicAuth(username, password)).text
products_json = json.loads(products_request)
products_df = pd.io.json.json_normalize(products_json, record_path='products').drop(['options', 'admin_graphql_api_id', 'body_html', 'image', 'images', 'vendor', 'published_scope', 'template_suffix'], axis = 1)

# products_df.shape
# products_df['variants'][0][0]['inventory_item_id']

products_df_concat = pd.concat([products_df, products_df.variants.apply(pd.Series)], axis =1).drop('variants', axis = 1)
products_df_melt = products_df_concat.melt(id_vars=products_df_concat.columns[:-8]).rename(columns = {'id': 'id_1', 'title': 'title_1'} ).dropna(subset = ['created_at'])

# Expand value column (dict entries) into multiple columns using pd.Series apply function
products_df_melt.value.apply(pd.Series)
products_df_melt = pd.concat([products_df_melt, products_df_melt.value.apply(pd.Series)], axis =1 , join = 'outer')# .drop(['index', 'value', 'id_1'], axis =1 )

# To convert numbers stored in scientific notation into legible text strings
def try_float(x):
    try:
        return str(format(float(x), '.0f'))
    except ValueError as e:
        return x

products_df_melt['id'] = products_df_melt['id'].apply(try_float).astype('str')
products_df_melt['image_id'] = products_df_melt['image_id'].apply(try_float).astype('str')
products_df_melt['inventory_item_id'] = products_df_melt['inventory_item_id'].apply(try_float).astype('str')
products_df_melt['sku'] = products_df_melt['sku'].replace(r'\s+',np.NaN,regex=True).replace('',np.nan)
products_df_melt['sku'] = products_df_melt['sku'].fillna(products_df_melt['title'])
products_df_melt = products_df_melt.dropna(subset = ['admin_graphql_api_id', 'value'])
# products_df_melt[products_df_melt['id_1'] == 8343952818224]

# To double check for accuracy for a single id_1
# products_df_melt_single = products_df_melt[products_df_melt['id_1'] == 162811740208]
# products_df_melt_single = pd.concat([products_df_melt_single, products_df_melt_single.value.apply(pd.Series)], axis =1 , join = 'outer')# .drop(['index', 'value', 'id_1'], axis =1 )

# To double check that NaNs have been replaced correctly at the "Default Title" rows
# PCMY has custom bundles that do not have an SKU number assigned
# products_df_melt[products_df_melt['title'] =='Default Title']


# url_inventory_levels = 'https://paulas-choice-malaysia.myshopify.com/admin/inventory_levels.json?location_ids=4181033008&limit=250'

inventory_levels_all = pd.DataFrame()
loop_count = 2 # how to derive this number from the length of products and length of location IDs?
for loop in range(loop_count):
    url_inventory_levels = 'https://paulas-choice-malaysia.myshopify.com/admin/inventory_levels.json?location_ids=4181033008&limit=250&page={}'.format(loop+1)
    inventory_levels_request = requests.get(url_inventory_levels,  auth=HTTPBasicAuth(username, password)).text
    inventory_levels_json = json.loads(inventory_levels_request)
    inventory_levels_df_part = pd.io.json.json_normalize(inventory_levels_json, record_path='inventory_levels')
    inventory_levels_all = inventory_levels_all.append(inventory_levels_df_part)

inventory_levels_all = inventory_levels_all.drop('admin_graphql_api_id', axis = 1)

# For double check
# inventory_levels_all[inventory_levels_all['inventory_item_id'] == 7120058187824]

products_with_inventory = pd.merge(inventory_levels_all, products_df_melt, how='outer', on='inventory_item_id')
# products_with_inventory.to_excel('products_with_inventory.xlsx')

# [{'id': 842864328752, 'product_id': 550253953072, 'name': 'Volume', 'position': 1, 'values': ['14 ml']}]

count_df  = inventory_levels_df.groupby('inventory_item_id').count()
len(count_df[count_df['available']>1]) #why are there multiple products in the same snapshot?
len(inventory_levels_df)
