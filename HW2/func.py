import aiohttp
import json
from config import OPEN_WEATHER_API_KEY
import requests


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

#Получаем данные о погоде в городе
async def weather_in_city(city):
    # получаем географические координаты города
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPEN_WEATHER_API_KEY}'
    geoloc = await fetch_data(url)
    geoloc = json.loads(geoloc)
    lat = geoloc[0]['lat']
    lon = geoloc[0]['lon']
    # получаем погодные данные
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={OPEN_WEATHER_API_KEY}'
    # url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API_KEY}'
    weather = await fetch_data(url)
    weather = json.loads(weather)
    return weather

#Получаем данные о калорийности продуктов
def get_food_info(product_name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        if products:  # Проверяем, есть ли найденные продукты
            first_product = products[0]
            return {
                'name': first_product.get('product_name', 'Неизвестно'),
                'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
            }
        return None
    print(f"Ошибка: {response.status_code}")
    return None
