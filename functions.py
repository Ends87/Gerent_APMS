from PIL import Image
import requests
import logging
import pytesseract
import data_identify
import mysql.connector
import json

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
        logging.error(f"Erro ao baixar a imagem: {e}", exc_info=True)

def download_pdf(bot, telegram_token, message):
    # obter o ID do arquivo do PDF
    pdf_message = message.document.file_id

    try:
        # Obter informações sobre o arquivo PDF
        logging.info("Obtendo informações sobre o arquivo PDF...")
        file_info = bot.get_file(pdf_message)
        file_path = file_info.file_path

        # Fazer o download do PDF
        logging.info("Fazendo download do arquivo PDF...")
        response = requests.get(f"https://api.telegram.org/file/bot{telegram_token}/{file_path}")
        response.raise_for_status()

        # Caminho da pasta "pdfs"
        path = "pdfs/"

        # Salvar o arquivo PDF
        path += f"{pdf_message}.pdf"
        with open(path, "wb") as new_file:
            new_file.write(response.content)

        return path

    except Exception as e:
        bot.reply_to(message, "Erro ao baixar o arquivo PDF")
        logging.error(f"Erro ao baixar o arquivo PDF: {e}", exc_info=True)

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

        data_identify.salva_dados(bot, texto, message_id, chat_id)

        comprovante = data_identify.diferenciar_comprovante(texto, message, bot)

        # Processar o texto com o Spacy
        logging.info("Processando texto com o Spacy...")
        doc = nlp(texto)

        # Monta a mensagem a ser enviada
        mensagem = f'Data da transação: {data_identify.buscar_datas(texto)}\n'
        mensagem += f'CNPJ do SELS: {data_identify.busca_cpnj(texto)}\n'
        mensagem += f'Valor enviado: {data_identify.busca_valor(texto)}\n'

        if comprovante == "Cartão de Débito" or comprovante == "Cartão de Crédito":
            mensagem += f'Autorização da transação: {data_identify.buscar_aut(texto)}\n'
            mensagem += f'Quantidade de parcelas: {data_identify.identificar_parcelas(texto)}'

        if comprovante == "Transferência Pix":
            mensagem += f'ID da transação: {data_identify.busca_ID(texto)}'

        # Envia a mensagem pelo bot
        bot.reply_to(message, mensagem)
        logging.debug(f'Mensagem enviada: {mensagem}')

    except Exception as e:
        bot.reply_to(message, "Erro ao processar a imagem")
        logging.error(f"Erro ao processar a imagem: {e}", exc_info=True)


def document_process(bot, telegram_token, message, nlp):

    # obter o ID da mensagem do Telegram, do chat correspondente e do arquivo da foto
    chat_id = message.chat.id
    message_id = message.message_id

    try:
        path = download_pdf(bot, telegram_token, message)

        # Extrair o texto da imagem com o pytesseract
        logging.info("Extraindo texto do PDF...")
        texto = data_identify.ler_pdf(path)
        logging.debug(f"Texto extraído da imagem: {texto}")

        data_identify.salva_dados(bot, texto, message_id, chat_id)

        comprovante = data_identify.diferenciar_comprovante(texto, message, bot)

        # Processar o texto com o Spacy
        logging.info("Processando texto com o Spacy...")
        doc = nlp(texto)

        # Monta a mensagem a ser enviada
        mensagem = f'Data da transação: {data_identify.buscar_datas(texto)}\n'
        mensagem += f'CNPJ do SELS: {data_identify.busca_cpnj(texto)}\n'
        mensagem += f'Valor enviado: {data_identify.busca_valor(texto)}\n'

        if comprovante == "Cartão de Débito" or comprovante == "Cartão de Crédito":
            mensagem += f'Autorização da transação: {data_identify.buscar_aut(texto)}\n'

        if comprovante == "Transferência Pix":
            mensagem += f'ID da transação: {data_identify.busca_ID(texto)}'

        # Envia a mensagem pelo bot
        bot.reply_to(message, mensagem)
        logging.debug(f'Mensagem enviada: {mensagem}')

    except Exception as e:
        bot.reply_to(message, "Erro ao processar a imagem")
        logging.error(f"Erro ao processar a imagem: {e}", exc_info=True)


def enviar_atualizacao(bot):
    novo_comando = '/saldo'
    id_usuario = 1034309995

    bot.send_message(id_usuario, "🥳")

    mensagem = f"Foi adicionado um novo comando: {novo_comando}! \nAgora você pode obter o relatório atualizado. Para acessá-lo, basta digitar '{novo_comando}' no chat.\n\nObs: Esta mensagem é destinada especialmente para administradores."

    bot.send_message(id_usuario, mensagem)


def send_file(response, file_name, bot, message):
    owner_id = "803998885"
    # Verificar se o arquivo não está vazio
    if response.status_code != 200:
        bot.send_message(message.chat.id, "Desculpe, não foi possível acessar o arquivo solicitado. Já notificamos o administrador e em breve o serviço voltará a suas atividades. Por favor, tente novamente mais tarde.")
        bot.send_message(owner_id, "‼️")
        bot.send_message(owner_id, "‼️ O token de acesso expirou. ‼️")
        return

    # Salvar o arquivo com o ID do usuário do telegram na pasta 'razao'
    with open(file_name, 'wb') as file:
        file.write(response.content)
        bot.send_document(message.chat.id, open(file_name, 'rb'))


def mysql_connector(bot, message):
    # Lê o arquivo carrega os dados de configuração do Banco de Dados em um dicionário
    with open('config/sql_config.json') as file:
        config = json.load(file)
    try:
        # Crie uma conexão com o banco de dados
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        return conn
    except mysql.connector.Error as error:
        # Se ocorrer algum erro ao conectar ao banco de dados, envie uma mensagem de erro
        bot.send_message(message.chat.id, f"Ocorreu um erro ao obter as informações do usuário: {error}")
        return


def get_params_colporteur(bot, message):
    # Faz a consulta no banco de dados para obter as informações do usuário
    try:
        # Crie um cursor para executar as consultas
        conn = mysql_connector(bot, message)
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
                "access_token": "7c6319f9b602334195237d0f71352119",
                "DenominationalEntityId": "c10dd043-e46d-e511-bbf3-002590396224"
            }
            return params
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
