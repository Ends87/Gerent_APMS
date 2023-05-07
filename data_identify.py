import os
import logging
import re
import requests
from dateutil import parser
import pytesseract
from PIL import Image
import json
from unidecode import unidecode

def dowload_image(bot, telegram_token, message):

    # obter o ID do arquivo da foto
    photo_message = message.photo[-1].file_id

    try:
        # Obter informações sobre o arquivo de imagem
        logging.info("Obtendo informações sobre o arquivo de imagem...")
        file_info = bot.get_file(photo_message)
        file_path = file_info.file_path

        # Fazer o download da imagem em sua resolução original
        logging.info("Fazendo download da imagem em sua resolução original...")
        response = requests.get(f"https://api.telegram.org/file/bot{telegram_token}/{file_path}")
        response.raise_for_status()

        # Caminho da pasta "imgs"
        path = "imgs/"

        # Salvar a imagem com maior resolução e qualidade
        path += f"{photo_message}.jpg"
        with open(path, "wb") as new_file:
            new_file.write(response.content)

        # Redimensionar a imagem para uma largura e altura maiores
        img = Image.open(path)
        largura = 800
        altura = int(largura * img.size[1] / img.size[0])
        img = img.resize((largura, altura))

        # Salvar a imagem com 300dpi e 100% da qualidade
        img.save(path, dpi=(300, 300), quality=100)
        return img
    except Exception as e:
        bot.reply_to(message, "Erro ao baixar a imagem")
        logging.error(f"Erro ao processar a imagem: {e}", exc_info=True)

def diferenciar_comprovante(texto, message, bot):
    texto = unidecode(texto.lower())
    if "pix" in texto and ("transacao" in texto or "transferencia" in texto):
        bot.reply_to(message, "Comprovante de Transferência Pix")
    elif "parcelado" in texto and "credito" in texto:
        bot.reply_to(message, "Comprovante de Cartão")
    else:
        bot.reply_to(message, "Não foi possível diferenciar o comprovante")

def extrair_aut(texto):
    regex_aut_ = re.compile(r'(?:AUT=|aut:)(\d+)')
    aut_nums = re.findall(regex_aut_, texto)
    return aut_nums
def busca_valor(texto):
    # Expressão regular para buscar por valores monetários
    regex_valor = re.compile(r"[Rr][Ss]?\s*\$?\s*\d{1,3}(?:[\.,]\d{3})*(?:,\d{2})?")

    # Busca por valores monetários no texto
    valor_enviado_str = regex_valor.findall(texto)

    # Converte a string do valor_enviado para float
    try:
        valor_enviado = float(
            valor_enviado_str[0].replace("R$ ", "").replace("RS ", "").replace(".", "").replace(",", "."))
    except ValueError:
        valor_enviado = None  # ou outra ação para tratar o erro
    return valor_enviado

def busca_cpnj(texto):
    # Expressão regular para buscar o CNPJ
    regex_cnpj = re.compile(r"0?4[.,/]?930[.,/]?244[|/]?0136[.,/-]?17")

    # Busca pelo CNPJ no texto
    cnpj_encontrado = regex_cnpj.search(texto)

    if cnpj_encontrado:
        cnpj_encontrado = ("SELS participou da transferencia")
    else:
        cnpj_encontrado = ("O CNPJ 04.930.244/0136-17 não foi encontrado no comprovante.")
    return cnpj_encontrado

def busca_ID(texto):
    # Expressão regular para buscar pelo ID da transação
    regex_id = re.compile(r"^[E£]\d{12}(?:\d{6}[se]\w{8}|\d{6}[se]\d{2}\w{7})$")

    # Busca pelo ID da transação no texto
    id_transacao = regex_id.search(texto)

    # Verifica se o ID da transação foi encontrado
    if id_transacao:
        id_transacao = id_transacao.group()
    else:
        id_transacao = ("ID da transação não encontrado.")
    return id_transacao

def salva_dados(bot, texto, message_id, chat_id):
    # carregar o dicionário de dados do arquivo JSON
    if os.path.exists('dados.json'):
        with open('dados.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    # verificar se o texto já está presente nos dados
    if texto not in data.values():
        # adicionar o novo texto ao dicionário
        data[message_id] = texto

        # escrever o dicionário atualizado no arquivo JSON
        with open('dados.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # enviar uma mensagem de confirmação ao usuário
        bot.send_message(chat_id=chat_id, text=f'Texto registrado com sucesso.')
    else:
        bot.send_message(chat_id=chat_id, text=f'Já registrado anteriormente.')

    # salva o dicionário em um arquivo json
    with open('dicionario.json', 'w') as f:
        json.dump(data, f)

def photo_process(bot, telegram_token, message, nlp):

    # Configura o caminho para o executável do Tesseract OCR
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # obter o ID da mensagem do Telegram, do chat correspondente e do arquivo da foto
    chat_id = message.chat.id
    message_id = message.message_id

    try:
        img = dowload_image(bot, telegram_token, message)

        # Extrair o texto da imagem com o pytesseract
        logging.info("Extraindo texto da imagem com o pytesseract...")
        texto = pytesseract.image_to_string(img)
        logging.debug(f"Texto extraído da imagem: {texto}")

        salva_dados(bot, texto, message_id, chat_id)

        diferenciar_comprovante(texto, message, bot)

        # Processar o texto com o Spacy
        logging.info("Processando texto com o Spacy...")
        doc = nlp(texto)

        # Inicializar as variáveis
        data_transacao = None
        autorizacao_transacao = None
        id_transacao = None

        # Identificar as datas no texto
        # Expressões regulares para diferentes formatos de data
        regex_data1 = r"\d{1,2}/\d{1,2}/\d{2,4}"  # formato dd/mm/aa ou dd/mm/aaaa
        regex_data2 = r"\d{1,2}\sde\s[a-z]+\sde\s\d{2,4}"  # formato dd de mês de aaaa
        regex_data3 = r"\d{1,2}\s[a-z]+\s\d{2,4}"  # formato dd mês aaaa
        regex_data4 = re.compile(r'\d{1,2}\s(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)\s\d{2}(?:\d{2})?', flags=re.IGNORECASE) # formato dd MÊS aaaa

        # Lista para armazenar as datas encontradas
        datas_encontradas = []

        # Procura pelas datas no texto
        for regex in [regex_data1, regex_data2, regex_data3, regex_data4]:
             datas_encontradas.extend(re.findall(regex, texto.lower()))

        print(datas_encontradas)

        # Verifica se as datas encontradas são válidas
        for data in datas_encontradas:
            try:
                parser.parse(data)
                data_transacao = data
            except:
                 pass

        cnpj_encontrado = busca_cpnj(texto)

        valor_enviado = busca_valor(texto)

        id_transacao = busca_ID(texto)

        # Monta a mensagem a ser enviada
        mensagem = f'Data da transação: {data_transacao}\n'
        mensagem += f'CNPJ do SELS: {cnpj_encontrado}\n'
        mensagem += f'Valor enviado: {valor_enviado}\n'
        mensagem += f'Autorização da transação: {autorizacao_transacao}\n'
        mensagem += f'ID da transação: {id_transacao}'

        # Envia a mensagem pelo bot
        bot.reply_to(message, mensagem)
        logging.debug(f'Mensagem enviada: {mensagem}')

    except Exception as e:
        bot.reply_to(message, "Erro ao processar a imagem")
        logging.error(f"Erro ao processar a imagem: {e}", exc_info=True)
