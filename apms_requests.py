import json
import os
import functions
import requests
from requests.structures import CaseInsensitiveDict


def login():
    url = 'https://apms.sdasystems.org/login'
    headers = CaseInsensitiveDict()
    headers.update({
        'Host': 'apms.sdasystems.org',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Brave";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Sec-GPC': '1',
        'Accept-Language': 'pt-BR,pt;q=0.7',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cookie': 'APMS='
    })

    response = requests.get(url, headers=headers)

    # Converter CaseInsensitiveDict para dicionário com chaves e valores em string
    headers_dict = {str(key): str(value) for key, value in response.headers.items()}

    # Armazenar a resposta em um dicionário
    response_data = {
        'status_code': response.status_code,
        'headers': headers_dict,
        'content': response.content.decode('utf-8')
    }

    # Armazenar a resposta em um arquivo JSON
    with open('response.json', 'w') as file:
        json.dump(response_data, file)

    # Imprimir o conteúdo da página
    print(response.content.decode('utf-8'))

    # # Dados da solicitação POST
    # url_post = 'https://apms.sdasystems.org/Login'
    # headers_post = {
    #     'Content-Type': 'application/x-www-form-urlencoded',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    #     # Outros cabeçalhos necessários
    # }
    # data_post = {
    #     'username': 'andersonavlis@outlook.com',
    #     'password': 'Zd6p',
    #     'btnLogin': '',
    # }
    #
    # # Criar uma sessão de solicitação
    # session = requests.Session()
    # session.headers.update(headers_post)
    #
    # # Enviar solicitação POST
    # response_post = session.post(url_post, data=data_post)
    #
    # # Dados da solicitação GET
    # url_get = 'https://login.sdasystems.org/connect/authorize?client_id=26f3b882-c847-42ab-90c0-064ab380b594&redirect_uri=https%3A%2F%2Fapms.sdasystems.org%2FCallback&response_type=id_token%20token&scope=openid%20profile%20email%20apms&state=7d98129081d24572a47a3cfdf9e25dc9&nonce=ee235a6fd854404e83deef784fe18851'
    # headers_get = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    #     # Outros cabeçalhos necessários
    # }
    #
    # # Atualizar cabeçalhos para a solicitação GET
    # session.headers.update(headers_get)
    #
    # # Enviar solicitação GET
    # response_get = session.get(url_get, stream=True)
    #
    # # Manipular a resposta
    # print(response_post.status_code)  # Código de status da resposta POST
    # print(response_get.status_code)  # Código de status da resposta GET
    #
    # # Exibir a resposta bruta
    # print(response_post.raw.read().decode('utf-8'))  # Conteúdo da resposta POST
    # print(response_get.raw.read().decode('utf-8'))  # Conteúdo da resposta GET
    #
    # # Extrair o token de acesso
    # pattern = r'access_token=([^&]+)'
    # match = re.search(pattern, response_get.text)
    # if match:
    #     access_token = match.group(1)
    #     print(f"Token de acesso: {access_token}")
    # else:
    #     print("Não foi possível encontrar o token de acesso.")

    return  #response_get.text


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


def get_all_colporteur_closure_report(bot, message):
    # Obtenha todos os parâmetros dos colportores
    params_list, colporteur_names = functions.get_all_params_colporteur(bot, message)

    url = 'https://apms.sdasystems.org//Reporting/Report/ColporteurClosureReport'
    headers = get_headers()

    # Itera sobre os parâmetros dos colportores
    for params, colporteur_name in zip(params_list, colporteur_names):
        # Faz a solicitação para o relatório do colportor
        response = requests.get(url, params=params, headers=headers)

        # Cria a pasta 'razao' se ela não existir
        if not os.path.exists('razao'):
            os.makedirs('razao')

        # Salva e envia o arquivo para o colportor atual
        file_name = f'razao/{colporteur_name}.pdf'
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
