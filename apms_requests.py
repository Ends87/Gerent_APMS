import logging
import requests
import json
import os

# Lê o arquivo carrega os dados de acesso a APMS em um dicionário
with open('config/apms_login.json') as f:
    config = json.load(f)


def login():
    # URL do formulário de login
    login_url = 'https://apms.sdasystems.org/Login'

    # Credenciais de login
    username = config['login_email']
    password = config['login_password']

    # Criando sessão de login
    with requests.session() as session:
        # Enviar solicitação POST com credenciais de login
        response = session.post(login_url, data={'username': username, 'password': password})

        # Verificar se o login foi bem-sucedido
        if response.status_code == 200:
            logging.info('Login bem-sucedido!')
        else:
            logging.info('Falha ao fazer login')


def obter_token_autorizacao():
    url = "https://apms.sdasystems.org/Callback"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://apms.sdasystems.org/CampaignReport",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Authorization": "c3a4bda14b3c5fc0a5b09a43b8d95a8d",
        "DenominationalEntityId": "c10dd043-e46d-e511-bbf3-002590396224"
    }

    response = requests.post(url, headers=headers)
    print(response.headers)
    token_autorizacao = response.headers.get("Authorization")

    if token_autorizacao:
        return token_autorizacao.split()[1]
    else:
        return None


def razao_request(bot, message):

    with open(f'dados_usuarios/{message.chat.id}.json', 'r') as file:
        params = json.load(file)

    url = 'https://apms.sdasystems.org//Reporting/Report/ColporteurClosureReport'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Referer': 'https://apms.sdasystems.org/CampaignReport',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cookie': 'APMS=; currentCultureSettings=%7B%22CultureCode%22%3A%22pt-BR%22%2C%22FormatDate%22%3A%22dd%2FMM%2Fyyyy%22%2C%22FormatTime%22%3A%22HH%3Amm%3Ass%22%2C%22NumberGroupSeparator%22%3A%22.%22%2C%22NumberDecimalSeparator%22%3A%22%2C%22%2C%22NumberDecimalDigits%22%3A2%2C%22CurrencyGroupSeparator%22%3A%22.%22%2C%22CurrencyDecimalDigits%22%3A2%2C%22CurrencyDecimalSeparator%22%3A%22%2C%22%2C%22TimeZoneInfoId%22%3A%22SA%20Eastern%20Standard%20Time%22%7D'
    }

    response = requests.get(url, params=params, headers=headers)

    # Criar a pasta 'razao' se ela não existir
    if not os.path.exists('razao'):
        os.makedirs('razao')

    # Chama a nova função para salvar o arquivo
    file_name = f'razao/{message.from_user.id}.pdf'
    send_file(response, file_name, bot, message)


def send_file(response, file_name, bot, message):
    # Salvar o arquivo com o ID do usuário do telegram na pasta 'razao'
    with open(file_name, 'wb') as file:
        file.write(response.content)
        bot.send_document(message.chat.id, open(file_name, 'rb'))

def get_balance_colporteurs_report(bot, message):
    url = "https://apms.sdasystems.org//Reporting/Report/BalanceColporteursReport?isExcel=false&isCsv=false&teamCampaignId=0990e8bf-6cf5-462d-a1ee-52bf2d2b1c79&campaignType=10&access_token=d63949e381da73d729a1313d7112252f&DenominationalEntityId=c10dd043-e46d-e511-bbf3-002590396224"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Referer": "https://apms.sdasystems.org/CampaignReport",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Cookie": "APMS=; currentCultureSettings=%7B%22CultureCode%22%3A%22pt-BR%22%2C%22FormatDate%22%3A%22dd%2FMM%2Fyyyy%22%2C%22FormatTime%22%3A%22HH%3Amm%3Ass%22%2C%22NumberGroupSeparator%22%3A%22.%22%2C%22NumberDecimalSeparator%22%3A%22%2C%22%2C%22NumberDecimalDigits%22%3A2%2C%22CurrencyGroupSeparator%22%3A%22.%22%2C%22CurrencyDecimalDigits%22%3A2%2C%22CurrencyDecimalSeparator%22%3A%22%2C%22%2C%22TimeZoneInfoId%22%3A%22SA%20Eastern%20Standard%20Time%22%7D"
    }
    response = requests.get(url, headers=headers)
    # Criar a pasta 'razao' se ela não existir
    if not os.path.exists('relatorios'):
        os.makedirs('relatorios')

    # Chama a nova função para salvar o arquivo
    file_name = f'relatorios/{message.from_user.id}.pdf'
    send_file(response, file_name, bot, message)
