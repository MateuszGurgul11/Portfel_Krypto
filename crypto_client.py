import requests

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
    
    # Wykonanie zapytania HTTP
    response = requests.get(url, params=params)
    
    # Sprawdzenie, czy odpowiedź jest poprawna (kod odpowiedzi HTTP 200)
    if response.status_code == 200:
        # Parsowanie danych JSON z odpowiedzi
        data = response.json()
        # Zwrócenie listy zawierającej dane o kryptowalutach
        return data
    else:
        # Jeśli wystąpił błąd, zwróć pustą listę
        return []
    
def get_crypto_curency_icon(coin_id):
    base_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    

def get_market_info():
    url = "https://api.coingecko.com/api/v3/global"
    response = requests.get(url)
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