import logging
import requests
import json
import os
import functions


def login():
    # Lê o arquivo carrega os dados de acesso a APMS em um dicionário
    with open('config/apms_login.json') as f:
        config = json.load(f)

    # URL do formulário de login
    login_url = 'https://apms.sdasystems.org/Login'

    # Criando sessão de login
    with requests.session() as session:
        # Enviar solicitação POST com credenciais de login
        response = session.post(login_url, data={'username': config['login_email'], 'password': config['login_password']})

        # Verificar se o login foi bem-sucedido
        if response.status_code == 200:
            logging.info('Login bem-sucedido!')
        else:
            logging.info('Falha ao fazer login')


def fazer_requisicao_autorizacao():
    client_id = "26f3b882-c847-42ab-90c0-064ab380b594"
    redirect_uri = "https://apms.sdasystems.org/Callback"
    response_type = "id_token token"
    scope = "openid profile email apms"
    nonce = "2378778c8e544672971993f4d91ed668"

    # Informações da requisição
    url = "https://login.sdasystems.org/authorize"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Referer": "https://login.sdasystems.org/login?signin=4344fd9bbc1f7359f6699d5ab11d57a3"
    }
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "response_type": response_type,
        "nonce": nonce
    }

    # Faz a requisição
    response = requests.get(url, headers=headers, params=params)

    # Salva o token de acesso
    token = response.json().get("access_token")
    return token


def get_headers():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Referer': 'https://apms.sdasystems.org/CampaignReport',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cookie': 'APMS=; currentCultureSettings=%7B%22CultureCode%22%3A%22pt-BR%22%2C%22FormatDate%22%3A%22dd%2FMM%2Fyyyy%22%2C%22FormatTime%22%3A%22HH%3Amm%3Ass%22%2C%22NumberGroupSeparator%22%3A%22.%22%2C%22NumberDecimalSeparator%22%3A%22%2C%22%2C%22NumberDecimalDigits%22%3A2%2C%22CurrencyGroupSeparator%22%3A%22.%22%2C%22CurrencyDecimalDigits%22%3A2%2C%22CurrencyDecimalSeparator%22%3A%22%2C%22%2C%22TimeZoneInfoId%22%3A%22SA%20Eastern%20Standard%20Time%22%7D'
    }

    return headers


def get_colporteur_closure_report(bot, message):
    # Busca os dados do colportor no banco de dados
    params = functions.get_params_colporteur(bot, message)

    url = 'https://apms.sdasystems.org//Reporting/Report/ColporteurClosureReport'

    headers = get_headers()

    response = requests.get(url, params=params, headers=headers)

    # Criar a pasta 'razao' se ela não existir
    if not os.path.exists('razao'):
        os.makedirs('razao')

    # Chama a nova função para salvar e enviar o arquivo
    file_name = f'razao/{message.from_user.id}.pdf'
    functions.send_file(response, file_name, bot, message)


def get_balance_colporteurs_report(bot, message):
    url = "https://apms.sdasystems.org//Reporting/Report/BalanceColporteursReport"

    # Lê o arquivo carrega os dados de configuração do Relatório em um dicionário
    with open('config/saldo.json') as file:
        params = json.load(file)

    headers = get_headers()

    response = requests.get(url, params=params, headers=headers)

    # Criar a pasta 'relatorios' se ela não existir
    if not os.path.exists('relatorios'):
        os.makedirs('relatorios')

    # Chama a nova função para salvar e enviar o arquivo
    file_name = f'relatorios/{message.from_user.id}.pdf'
    functions.send_file(response, file_name, bot, message)
