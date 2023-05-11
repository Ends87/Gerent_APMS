import telebot
import apms_requests
import data_identify
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

# Lê o arquivo e carrega o token do telegram em um dicionário
with open('config/telegram_token.json') as f:
    config = json.load(f)

# Obtém o valor do token do Telegram a partir do dicionário
telegram_token = config['telegram_token']

bot = telebot.TeleBot(telegram_token)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Nosso bot do Telegram lê comprovantes de Pix e Cartão de Crédito e gera a Razão Atualizada em um click (/razao). Está em versão inicial e não suporta todos os bancos. Use PicPay para aproveitar todas as funcionalidades.")
    data_identify.verificar_usuario(bot, message)


@bot.message_handler(commands=['razao'])
def start_connection(message):
    if data_identify.verificar_usuario(bot, message):
        bot.send_message(message.chat.id, "Carregando Razão")
        apms_requests.login()
        apms_requests.razao_request(bot, message)


@bot.message_handler(content_types=['text', 'sticker', 'audio'])
def start_connection(message):
    bot.reply_to(message, "Para um melhor aproveitamento das funcionalidades do nosso bot do Telegram, é importante salientar que ele não aceita mensagens do tipo texto, áudio e sticker. Por isso, recomendamos que os usuários enviem o comando /razao ou para obter a razão compartilhem comprovantes no formato de imagem ou PDF para que seja realizado o lançamento. Utilize o bot de forma otimizada e tenha mais eficiência em suas tarefas!")
    data_identify.verificar_usuario(bot, message)


@bot.message_handler(content_types=['document'])
def document_process(message):
    if data_identify.verificar_usuario(bot, message):
        file_info = bot.get_file(message.document.file_id)
        bot.download_file(file_info.file_path)

        # verifica se o arquivo é um PDF
        _, file_ext = os.path.splitext(file_info.file_path)
        if file_ext.lower() == '.pdf':
            # processa o arquivo PDF
            functions.document_process(bot, telegram_token, message, nlp)
        else:
            bot.reply_to(message, "Apenas arquivos PDF são suportados.")


@bot.message_handler(content_types=['photo'])
def photo_process(message):
    if data_identify.verificar_usuario(bot, message):
        functions.photo_process(bot, telegram_token, message, nlp)


bot.polling()
