import matplotlib.pyplot as plt
import seaborn as sns
import aiohttp
import json
import asyncio
import datetime
WINDOW_SIZE=30


def analizer(data, city):
    #вычисление скользящего среднего и отклонения
    df = data[data['city']==city]
    df ['moving_avarage']  = df['temperature'].rolling(WINDOW_SIZE).mean()
    df ['std']  = df['temperature'].rolling(WINDOW_SIZE).std()
    return df


def plot(df, city, real=False, ma=False, sigma=False, outliers=False):
    f, axs = plt.subplots(figsize=(22, 6))
    plt.title(city)
    if real:
        sns.lineplot(data=df, x="timestamp", y="temperature", color="royalblue", ax=axs, label="temperature")
    if sigma:
        plt.fill_between(x=df["timestamp"], y1=df["moving_avarage"]-2*df['std'], y2=df["moving_avarage"]+2*df['std'], color='lightskyblue')
    if ma:
        sns.lineplot(data=df, x="timestamp", y="moving_avarage", color="darkblue", ax=axs, label="moving_avarage")
    if outliers:
        sns.scatterplot(x=df['timestamp'], y=df.query('temperature > moving_avarage+2*std or temperature < moving_avarage-2*std')['temperature'], color='r', label='outlaers')
    plt.legend(loc="upper right")
    plt.show()
    return f


def get_season_profile(df, city):
    #профиль сезона: средняя температура и стандартное отклонение
    return df[df['city'] == city].groupby('season').agg({'temperature' : ['mean', 'std']})


def outlaers_by_season(df, city):
    #отрисовка аномалий по сезонам
    f, axs = plt.subplots(figsize=(16, 10))
    plt.title(city)
    plt.title(city)
    sns.boxplot(data= df[df['city'] == city], x="season", y="moving_avarage")
    sns.scatterplot(x=df[df['city'] == city]['season'], y=df[df['city'] == city].query('temperature > moving_avarage+2*std or temperature < moving_avarage-2*std')['temperature'], color='r', label='outlaers')
     
    return f


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
        
async def wether_in_city(city, API_KEY):
    #получаем географические координаты города
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}' 
    geoloc = await fetch_data(url)
    geoloc=json.loads(geoloc)
    lat=geoloc[0]['lat']
    lon=geoloc[0]['lon']
    #получаем погодные данные
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}'
    #url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API_KEY}'
    weather = await fetch_data(url)
    weather=json.loads(weather)
    return weather


month_to_season = {12: "winter", 1: "winter", 2: "winter",
                   3: "spring", 4: "spring", 5: "spring",
                   6: "summer", 7: "summer", 8: "summer",
                   9: "autumn", 10: "autumn", 11: "autumn"}


def anomaly_detecter(df, city, API_KEY):
    curr_temp=asyncio.run(wether_in_city(city, API_KEY))
    curr_season=month_to_season[datetime.datetime.now().month]
    upper_bound=get_season_profile(df, city)['temperature']['mean'].loc[curr_season]+2*get_season_profile(df, city)['temperature']['std'].loc[curr_season]
    lower_bound=get_season_profile(df, city)['temperature']['mean'].loc[curr_season]-2*get_season_profile(df, city)['temperature']['std'].loc[curr_season]
    if curr_temp['main']['temp'] > upper_bound or curr_temp['main']['temp'] < lower_bound: 
        return 'наблюдается аномальное значение температуры.'
    else:
        return 'температура в рамках нормы'