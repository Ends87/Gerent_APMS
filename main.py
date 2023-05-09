import telebot
import apms_requests
import functions
import spacy
import os
import logging
import json

# Configuração de logging
logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

# Baixa e carrega o modelo de linguagem português do spaCy
logging.info("Baixando e carregando o modelo de linguagem do spaCy...")
#spacy.cli.download("pt_core_news_sm")
nlp = spacy.load("pt_core_news_sm")
logging.info("Modelo de linguagem carregado com sucesso!")

# Lê o arquivo config.json e carrega o conteúdo em um dicionário
with open('config.json') as f:
    config = json.load(f)

# Obtém o valor do token do Telegram a partir do dicionário
telegram_token = config['telegram_token']

bot = telebot.TeleBot(telegram_token)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Estou pronto, basta me enviar a foto que deseja obter o texto!")

@bot.message_handler(content_types=['text', 'sticker', 'audio'])
def start_connection(message):
    apms_requests.login(bot, message)

@bot.message_handler(content_types=['document'])
def document_process(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # verifica se o arquivo é um PDF
    _, file_ext = os.path.splitext(file_info.file_path)
    if file_ext.lower() == '.pdf':
        # processa o arquivo PDF
        functions.document_process(bot, telegram_token, message, nlp)
    else:
        bot.reply_to(message, "Apenas arquivos PDF são suportados.")

@bot.message_handler(content_types=['photo'])
def photo_process(message):
    functions.photo_process(bot, telegram_token, message, nlp)

bot.polling()