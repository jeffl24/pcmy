
import shopify
import requests

import json
import datetime

username = '7e86d45b24d9a3da5da72a93a8210f34'
password = '3ddc548cff03ffd7d064c7e2fa7f3431'

shop_url = 'https://{}:{}@paulas-choice-singapore.myshopify.com/admin'.format(username, password)

shopify.ShopifyResource.set_site(shop_url)

session = shopify.Session("paulas-choice-singapore.myshopify.com")

shop =  shopify.Shop.current()

shopify_customer = shopify.Customer.count()

f=open("D:\\Code\pcmy\shopify_customer_count.txt", "a+")

f.write("{} {} \n".format(datetime.date.today(), shopify.Customer.count()))

f.close()

# alternative method
# from requests.auth import HTTPBasicAuth
# url_customers_count = 'https://paulas-choice-singapore.myshopify.com/admin/customers/count.json'
# products_request = requests.get(url_customers_count, auth=HTTPBasicAuth(username, password)).text
