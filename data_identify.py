import logging
import re
import requests
from dateutil import parser
import pytesseract
from PIL import Image

def photo_process(bot, telegram_token, message, nlp):
    # Obter a ID do arquivo da foto
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

        # Extrair o texto da imagem com o pytesseract
        logging.info("Extraindo texto da imagem com o pytesseract...")
        texto = pytesseract.image_to_string(img)
        logging.debug(f"Texto extraído da imagem: {texto}")

        # Processar o texto com o Spacy
        logging.info("Processando texto com o Spacy...")
        doc = nlp(texto)

        # Inicializar as variáveis
        data_transacao = None
        participante_a = None
        participante_b = None
        valor_enviado = None
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

        # Expressão regular para buscar o CNPJ
        regex_cnpj = re.compile(r"0?4[.-/]930[.-/]244[/-]0136[/-]17")

        # Busca pelo CNPJ no texto
        cnpj_encontrado = regex_cnpj.search(texto)

        if cnpj_encontrado:
            participante_a=("SELS participou da transferencia")
        else:
            participante_a=("O CNPJ 04.930.244/0136-17 não foi encontrado no comprovante.")

        # Expressão regular para buscar por valores monetários
        regex_valor = re.compile(r"R\$\s*\d+(?:\.\d{3})*(?:,\d{2})?")

        # Busca por valores monetários no texto
        valor_enviado_str = regex_valor.findall(texto)

        print(valor_enviado_str)

        # Converte a string do valor_enviado para float
        valor_enviado = float(valor_enviado_str[0].replace("R$ ", "").replace(".", "").replace(",", "."))



        # Expressão regular para buscar pelo ID da transação
        regex_id = re.compile(r"E\d{15}s[0-9a-f]{16}")

        # Busca pelo ID da transação no texto
        id_transacao = regex_id.search(texto)

        # Verifica se o ID da transação foi encontrado
        if id_transacao:
            id_transacao = id_transacao.group()
        else:
            id_transacao = ("ID da transação não encontrado.")

        # Monta a mensagem a ser enviada
        mensagem = f'Data da transação: {data_transacao}\n'
        mensagem += f'CNPJ do SELS: {participante_a}\n'
        mensagem += f'Participante B: {participante_b}\n'
        mensagem += f'Valor enviado: {valor_enviado}\n'
        mensagem += f'Autorização da transação: {autorizacao_transacao}\n'
        mensagem += f'ID da transação: {id_transacao}'

        # Envia a mensagem pelo bot
        bot.reply_to(message, mensagem)
        logging.debug(f'Mensagem enviada: {mensagem}')

    except Exception as e:
        bot.reply_to(message, "Erro ao processar a imagem")
        logging.error(f"Erro ao processar a imagem: {e}", exc_info=True)
