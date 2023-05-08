from PIL import Image
import requests
import logging
import pytesseract
import data_identify

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

        if comprovante == "Transferência Pix":
            mensagem += f'ID da transação: {data_identify.busca_ID(texto)}'

        # Envia a mensagem pelo bot
        bot.reply_to(message, mensagem)
        logging.debug(f'Mensagem enviada: {mensagem}')

    except Exception as e:
        bot.reply_to(message, "Erro ao processar a imagem")
        logging.error(f"Erro ao processar a imagem: {e}", exc_info=True)
