import requests
import pandas as pd
from requests.auth import HTTPBasicAuth #not always necessary
import json
import pprint

username = 'a8e0caf507870e4d91e140d75cb1e0c5'
password = '38b5c1a103fc779e956eab1436dc1934'

url_customers = 'https://paulas-choice-malaysia.myshopify.com/admin/customers.json'
customers_request = requests.get(url_customers, auth=HTTPBasicAuth(username, password)).text
customers_json = json.loads(customers_request)

customers_json.keys()

customers_df = pd.io.json.json_normalize(customers_json, record_path='products').drop(columns_to_drop, axis = 1)

customers_df = pd.io.json.json_normalize(customers_json, record_path='customers')

customers_df

import shopify

shop_url = 'https://{}:{}@paulas-choice-malaysia.myshopify.com/admin'.format(username, password)

shopify.ShopifyResource.set_site(shop_url)

session = shopify.Session("paulas-choice-malaysia.myshopify.com")

shop =  shopify.Shop.current()

customers_shopify = shopify.customer.Customer
customers_shopify
