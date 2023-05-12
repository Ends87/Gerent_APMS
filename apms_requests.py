import logging
import requests
import json
import os
import functions
import mysql.connector


def login():
    # Lê o arquivo carrega os dados de acesso a APMS em um dicionário
    with open('config/apms_login.json') as f:
        config = json.load(f)

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

    token_autorizacao = response.headers.get("Authorization")

    if token_autorizacao:
        return token_autorizacao.split()[1]
    else:
        return None


def razao_request(bot, message):
    # Lê o arquivo carrega os dados de acesso a APMS em um dicionário
    with open('config/sql_config.json') as f:
        config = json.load(f)

    # Faz a consulta no banco de dados para obter as informações do usuário
    try:
        # Crie uma conexão com o banco de dados
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )

        # Crie um cursor para executar as consultas
        cursor = conn.cursor()

        # Execute a consulta SQL para obter as informações do usuário
        query = f'SELECT isColporteur, colporteur_id FROM Usuario WHERE telegram_id = {message.from_user.id}'
        cursor.execute(query)
        result = cursor.fetchone()

        # Verifique se o usuário é um colportor e obtenha as informações necessárias
        if result[0]:
            query = f"SELECT team_campaign_id FROM Colporteur WHERE colporteur_id = '{result[1]}'"

            cursor.execute(query)

            team_campaign_id = cursor.fetchone()[0]
            params = {
                "isExcel": "false",
                "isCsv": "false",
                "isAnalytical": "true",
                "teamCampaignColporteurId": result[1],
                "teamCampaignId": team_campaign_id,
                "minimizedDataReport": "false",
                "campaignType": "10",
                "access_token": "9a423131485871857c23834181695dfc",
                "DenominationalEntityId": "c10dd043-e46d-e511-bbf3-002590396224"
            }
        else:
            # Caso contrário, envie uma mensagem informando que o usuário não é um colportor
            bot.send_message(message.chat.id, "Você não está registrado como um colportor.")
            return
    except mysql.connector.Error as error:
        # Se ocorrer algum erro ao conectar ao banco de dados, envie uma mensagem de erro
        bot.send_message(message.chat.id, f"Ocorreu um erro ao obter as informações do usuário: {error}")
        return
    finally:
        # Sempre feche o cursor e a conexão após a consulta
        cursor.close()
        conn.close()

    url = 'https://apms.sdasystems.org//Reporting/Report/ColporteurClosureReport'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Referer': 'https://apms.sdasystems.org/CampaignReport',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cookie': 'APMS=; currentCultureSettings=%7B%22CultureCode%22%3A%22pt-BR%22%2C%22FormatDate%22%3A%22dd%2FMM%2Fyyyy%22%2C%22FormatTime%22%3A%22HH%3Amm%3Ass%22%2C%22NumberGroupSeparator%22%3A%22.%22%2C%22NumberDecimalSeparator%22%3A%22%2C%22%2C%22NumberDecimalDigits%22%3A2%2C%22CurrencyGroupSeparator%22%3A%22.%22%2C%22CurrencyDecimalDigits%22%3A2%2C%22CurrencyDecimalSeparator%22%3A%22%2C%22%2C%22TimeZoneInfoId%22%3A%22SA%20Eastern%20Standard%20Time%22%7D'
    }

    response = requests.get(url, params=params, headers=headers)
    print(response)
    # Criar a pasta 'razao' se ela não existir
    if not os.path.exists('razao'):
        os.makedirs('razao')

    # Chama a nova função para salvar e enviar o arquivo
    file_name = f'razao/{message.from_user.id}.pdf'
    functions.send_file(response, file_name, bot, message)


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
    # Criar a pasta 'relatorios' se ela não existir
    if not os.path.exists('relatorios'):
        os.makedirs('relatorios')

    # Chama a nova função para salvar e enviar o arquivo
    file_name = f'relatorios/{message.from_user.id}.pdf'
    functions.send_file(response, file_name, bot, message)
