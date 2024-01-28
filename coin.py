import requests

def get_coin_data(coin_id = None):
    base_url = "https://api.coincap.io/v2/assets"
    if coin_id is not None:
        url = f"{base_url}/{coin_id}"
    else:
        url = base_url

    response = requests.get(url)
    if response.status_code == 200:
        coin_data = response.json()
        return coin_data
    else:
        return None
    
def get_rates_idr():
    base_url = "https://api.coincap.io/v2/rates"
    
    response = requests.get(base_url)
    if response.status_code == 200:
        rate = response.json()
        rate_idr = next((rate for rate in rate['data'] if rate["id"] == "indonesian-rupiah"),None)
        return rate_idr['rateUsd']
    else:
        return None
    
# {
#       "id": "indonesian-rupiah",
#       "symbol": "IDR",
#       "currencySymbol": "Rp",
#       "type": "fiat",
#       "rateUsd": "0.0000694494405456"
#     }