
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

url_products = 'https://paulas-choice-malaysia.myshopify.com/admin/products.json?limit=250'
products_request = requests.get(url_products, auth=HTTPBasicAuth(username, password)).text
products_json = json.loads(products_request)
products_df = pd.io.json.json_normalize(products_json, record_path='products').drop(['options', 'admin_graphql_api_id', 'body_html', 'image', 'images', 'vendor', 'published_scope', 'template_suffix', 'created_at', 'updated_at', 'published_at'], axis = 1)

# products_df.shape
# products_df['variants'][0][0]['inventory_item_id']

products_df_concat = pd.concat([products_df, products_df.variants.apply(pd.Series)], axis =1).drop('variants', axis = 1)
products_df_melt = products_df_concat.melt(id_vars=products_df_concat.columns[:-8])#.rename(columns = {'id': 'id_1', 'title': 'title_1'} )#.dropna(subset = ['created_at'])

# Expand value column (dict entries) into multiple columns using pd.Series apply function
# products_df_melt.value.apply(pd.Series)
products_df_melt = pd.concat([products_df_melt, products_df_melt.value.apply(pd.Series)], axis =1 , join = 'outer').drop(['value', 'admin_graphql_api_id', 'options'], axis = 1)# .drop(['index', 'value', 'id_1'], axis =1 )

products_df_melt = products_df_melt.dropna(subset = ['created_at'])

# To convert numbers stored in scientific notation into legible text strings
def try_float(x):
    try:
        return str(format(float(x), '.0f'))
    except ValueError as e:
        return x

# Convert columns in scientific notation to text
products_df_melt['id'] = products_df_melt['id'].apply(try_float).astype('str')
products_df_melt['image_id'] = products_df_melt['image_id'].apply(try_float).astype('str')
products_df_melt['product_id'] = products_df_melt['product_id'].apply(try_float).astype('str')
products_df_melt['inventory_item_id'] = products_df_melt['inventory_item_id'].apply(try_float).astype('str')

# Convert columns in text to numbers
products_df_melt['price'] = products_df_melt['price'].astype(float)

# Convert date-time columns to datetime format
products_df_melt['created_at'] = products_df_melt['created_at'].astype("datetime64[ns]")
# products_df_melt['published_at'] = products_df_melt['published_at'].astype("datetime64[ns]")
products_df_melt['updated_at'] = products_df_melt['updated_at'].astype("datetime64[ns]")

products_df_melt

products_df_melt['sku'] = products_df_melt['sku'].replace(r'\s+',np.NaN,regex=True).replace('',np.nan)
products_df_melt['sku'] = products_df_melt['sku'].fillna(products_df_melt['title'])
products_df_melt = products_df_melt.dropna(subset = ['admin_graphql_api_id', 'value'])

products_df_melt.drop(columns = ['value', 'admin_graphql_api_id', 'options'], axis =1)
# products_df_melt[products_df_melt['id_1'] == 8343952818224]

# To double check for accuracy for a single id_1
# products_df_melt_single = products_df_melt[products_df_melt['id_1'] == 162811740208]
# products_df_melt_single = pd.concat([products_df_melt_single, products_df_melt_single.value.apply(pd.Series)], axis =1 , join = 'outer')# .drop(['index', 'value', 'id_1'], axis =1 )

# To double check that NaNs have been replaced correctly at the "Default Title" rows
# PCMY has custom bundles that do not have an SKU number assigned
# products_df_melt[products_df_melt['title'] =='Default Title']
