import requests

API_KEY = "CG-JzztKy2joVKsnTBRYhzgNw5z"

def get_top_cryptocurrencies():
    # Adres URL punktu końcowego dla danych o najpopularniejszych kryptowalutach
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    
    # Parametry zapytania dla sortowania według kapitalizacji rynkowej i ograniczenia liczby wyników
    params = {
        'vs_currency': 'usd',  # Cena w USD
        'order': 'market_cap_desc',  # Sortuj według kapitalizacji rynkowej malejąco
        'per_page': 10,  # Ilość wyników do wyświetlenia (10 najpopularniejszych kryptowalut)
        'page': 1,  # Strona wyników
        'sparkline': False  # Wyłącz wykresy punktowe
    }
    
    headers = {
        "x-cg-pro-api-key": API_KEY
    }

    # Wykonanie zapytania HTTP
    response = requests.get(url, params=params, headers=headers)
    
    # Sprawdzenie, czy odpowiedź jest poprawna (kod odpowiedzi HTTP 200)
    if response.status_code == 200:
        # Parsowanie danych JSON z odpowiedzi
        data = response.json()
        cryptocurrencies_info = []
        for item in data:
            cryptocurrency = {
                'name' : item['name'],
                'symbol': item['symbol'],
                'current_price': item['current_price'],
                'icon_url': item['image']
            }
            cryptocurrencies_info.append(cryptocurrency)
        # Zwrócenie listy zawierającej dane o kryptowalutach
        return cryptocurrencies_info
    else:
        # Jeśli wystąpił błąd, zwróć pustą listę
        return []
    
def get_crypto_curency_icon(coin_id):
    base_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    headers = {
        "x-cg-pro-api-key": API_KEY
    }

    response = requests.get(base_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['image']['thumb']
    else:
        print("blad wyswietlania ikony")
        return None
    

def get_market_info():
    url = "https://api.coingecko.com/api/v3/global"
    headers = {
        "x-cg-pro-api-key": API_KEY
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        market_info = {}
        if "data" in data and "active_cryptocurrencies" in data["data"]:
            market_info["active_cryptocurrencies"] = data["data"]["active_cryptocurrencies"]
        else:
            market_info["active_cryptocurrencies"] = "N/A"
        return market_info
    else:
        print("Błąd w pobieraniu danych rynkowych")
        return None
    
def get_crypto_details(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    headers = {
        "x-cg-pro-api-key": API_KEY
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        crypto_details = {
            'id': data['id'],
            'symbol': data['symbol'],
            'name': data['name'],
            'description': data.get('description', {}).get('en', ''),
            'current_price': data['market_data']['current_price']['usd'],
            'market_cap': data['market_data']['market_cap']['usd'],
            'total_volume': data['market_data']['total_volume']['usd'],
            'high_24h': data['market_data']['high_24h']['usd'],
            'low_24h': data['market_data']['low_24h']['usd'],
            'price_change_24h': data['market_data']['price_change_24h_in_currency']['usd'],
            'price_change_percentage_24h': data['market_data']['price_change_percentage_24h'],
            'market_cap_rank': data['market_data']['market_cap_rank'],
            'coingecko_rank': data['coingecko_rank'],
            'coingecko_score': data['coingecko_score'],
            'developer_score': data['developer_score'],
            'community_score': data['community_score'],
            'liquidity_score': data['liquidity_score'],
            'public_interest_score': data['public_interest_score'],
            'icon_url': data['image']['thumb']
        }
        return crypto_details
    else:
        print(f"Błąd przy pobieraniu danych o walucie {coin_id}")
        return None