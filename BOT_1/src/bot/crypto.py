import os
import requests
from cryptography.fernet import Fernet

class CryptoProcessor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.cipher = Fernet(os.getenv('ENCRYPTION_KEY').encode())

    def generate_wallet(self, currency: str) -> dict:
        """Генерирует новый кошелек для указанной криптовалюты"""
        url = f"https://api.blockcypher.com/v1/{currency}/main/addrs"
        response = requests.post(url, params={'token': self.api_key})
        
        if response.status_code == 201:
            data = response.json()
            return {
                'address': data['address'],
                'private': self.cipher.encrypt(data['private'].encode()).decode()
            }
        raise Exception(f"Blockcypher API error: {response.text}")

    def check_payment(self, address: str, currency: str) -> bool:
        """Проверяет наличие подтвержденных платежей по адресу"""
        url = f"https://api.blockcypher.com/v1/{currency}/main/addrs/{address}/balance"
        response = requests.get(url, params={'token': self.api_key})
        
        if response.status_code == 200:
            return response.json().get('final_balance', 0) > 0
        return False