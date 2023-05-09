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

def data_filter():
    url = 'https://apms.sdasystems.org/CampaignReport'
    payload = {'filter': 'termo-de-busca'}
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        # Extrair os dados da resposta do servidor
        data = response.text
        # Fazer o parse do HTML para extrair os dados necessários
        # ...
    else:
        # Tratar o erro
        print('Erro ao fazer a solicitação HTTP')