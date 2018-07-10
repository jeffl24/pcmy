import shopify

API_KEY = 'a8e0caf507870e4d91e140d75cb1e0c5'
PASSWORD = '38b5c1a103fc779e956eab1436dc1934'
shop_url = "https://%s:%s@paulas-choice-malaysia.myshopify.com/admin" % (API_KEY, PASSWORD)
shopify.ShopifyResource.set_site(shop_url)

# Get the current shop
shop = shopify.Shop.current()

# Get a specific product
product = shopify.Locations.get(id = '4181033008')
product

# inventory_level = shopify.inventory_levels(location_ids = "7120058187824")
inventory_level = shopify.inventory_levels(location_ids = "4181033008")
inventory_level
