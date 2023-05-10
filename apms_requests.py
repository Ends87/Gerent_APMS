import requests
import json

# Lê o arquivo config.json e carrega o conteúdo em um dicionário
with open('config.json') as f:
    config = json.load(f)

def login(bot, message):
    # URL do formulário de login
    login_url = 'https://apms.sdasystems.org/Login'

    # Credenciais de login
    username = config['login_email']
    password = config['login_password']

    # Criando sessão de login
    with requests.Session() as session:
        # Enviar solicitação POST com credenciais de login
        response = session.post(login_url, data={'username': username, 'password': password})

        # Verificar se o login foi bem-sucedido
        if response.status_code == 200:
            bot.reply_to(message, 'Login bem-sucedido!')
        else:
            bot.reply_to(message, 'Falha ao fazer login')


def razao_request():
    import requests

    url = 'https://apms.sdasystems.org//Reporting/Report/ColporteurClosureReport'
    params = {
        'isExcel': 'false',
        'isCsv': 'false',
        'isAnalytical': 'true',
        'teamCampaignColporteurId': '2dd7e8c0-b1c0-4cbe-a9c5-e3e524f62b51',
        'teamCampaignId': '0990e8bf-6cf5-462d-a1ee-52bf2d2b1c79',
        'minimizedDataReport': 'false',
        'campaignType': '10',
        'access_token': '3d7fa480bd65706fb6f2a1677773bbc9',
        'DenominationalEntityId': 'c10dd043-e46d-e511-bbf3-002590396224'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Referer': 'https://apms.sdasystems.org/CampaignReport',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cookie': 'APMS=; currentCultureSettings=%7B%22CultureCode%22%3A%22pt-BR%22%2C%22FormatDate%22%3A%22dd%2FMM%2Fyyyy%22%2C%22FormatTime%22%3A%22HH%3Amm%3Ass%22%2C%22NumberGroupSeparator%22%3A%22.%22%2C%22NumberDecimalSeparator%22%3A%22%2C%22%2C%22NumberDecimalDigits%22%3A2%2C%22CurrencyGroupSeparator%22%3A%22.%22%2C%22CurrencyDecimalDigits%22%3A2%2C%22CurrencyDecimalSeparator%22%3A%22%2C%22%2C%22TimeZoneInfoId%22%3A%22SA%20Eastern%20Standard%20Time%22%7D'
    }

    response = requests.get(url, params=params, headers=headers)

    with open('arquivo.pdf', 'wb') as f:
        f.write(response.content)
