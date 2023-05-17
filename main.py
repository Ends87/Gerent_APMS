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
nlp = spacy.load("pt_core_news_sm")
logging.info("Modelo de linguagem carregado com sucesso!")

# Lê o arquivo e carrega o token do telegram
with open('config/telegram_token.json') as f:
    config = json.load(f)
telegram_token = config['telegram_token']

bot = telebot.TeleBot(telegram_token)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Nosso bot do Telegram lê comprovantes de Pix e Cartão de Crédito e gera a Razão Atualizada em um click (/razao). Está em versão inicial e não suporta todos os bancos. Use PicPay para aproveitar todas as funcionalidades.")
    data_identify.verificar_usuario(bot, message)


@bot.message_handler(commands=['razao', 'RAZAO'])
def start_connection(message):
    if data_identify.verificar_usuario(bot, message):
        bot.send_message(message.chat.id, "🐾")
        apms_requests.login()
        apms_requests.get_colporteur_closure_report(bot, message)


@bot.message_handler(commands=['saldo', 'SALDO'])
def get_balence(message):
    if message.chat.id == "1034309995" or "803998885":
        bot.send_message(message.chat.id, "💫")
        apms_requests.get_balance_colporteurs_report(bot, message)


@bot.message_handler(content_types=['text', 'sticker', 'audio'])
def treat_message_invalid(message):
    bot.reply_to(message, "Para um melhor aproveitamento das funcionalidades do nosso bot do Telegram, é importante salientar que ele não aceita mensagens do tipo texto, áudio e sticker. Por isso, recomendamos que os usuários enviem o comando /razao ou para obter a razão compartilhem comprovantes no formato de imagem ou PDF para que seja realizado o lançamento. Utilize o bot de forma otimizada e tenha mais eficiência em suas tarefas!")
    data_identify.verificar_usuario(bot, message)


@bot.message_handler(content_types=['document'])
def document_process(message):
    functions.document_process(bot, telegram_token, message)


@bot.message_handler(content_types=['photo'])
def photo_process(message):
    if data_identify.verificar_usuario(bot, message):
        functions.photo_process(bot, telegram_token, message)


bot.polling()
