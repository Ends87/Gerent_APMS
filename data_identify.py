import logging
import re
from datetime import datetime
from unidecode import unidecode
import PyPDF2
import mysql.connector
import json


def mysql_connector():
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
        # Se ocorrer algum erro ao conectar ao banco de dados, retorne o erro
        return error


def read_pdf(path):
    with open(path, 'rb') as f:
        reader_pdf = PyPDF2.PdfReader(f)
        num_pages = len(reader_pdf.pages)
        for page in range(num_pages):
            page_content = reader_pdf.pages[page]
            text = page_content.extract_text()
    return text


def diferenciar_comprovante(text, message, bot):
    text = unidecode(text.lower())
    if "pix" in text or "99Pay" in text:
        logging.info("Comprovante de Transferência Pix")
        bot.reply_to(message, "Comprovante de Transferência Pix")
        return "Transferência Pix"
    elif "parcelado" in text:
        logging.info("Comprovante de Cartão de Crédito")
        bot.reply_to(message, "Comprovante de Cartão de Crédito")
        return "Cartão de Crédito"
    elif "debito a vista" in text:
        logging.info("Comprovante de Cartão de Débito")
        bot.reply_to(message, "Comprovante de Cartão de Débito")
        return "Cartão de Débito"
    else:
        logging.warning("Não foi possível diferenciar o comprovante")
        bot.reply_to(message, "Não foi possível diferenciar o comprovante")
        return "Não foi possível diferenciar o comprovante"


def search_aut(texto):
    regex_aut = re.compile(r"AUT\s*=\s*(\d{6})\b|aut\s*:\s*(\d{6})\b|Autoriza[gçc][aã]o\s*:\s*(\d{6})\b", re.IGNORECASE)
    aut = re.findall(regex_aut, texto)
    aut = [num for tup in aut for num in tup if num.isdigit()]

    # Verifica se há pelo menos um número de autorização
    if aut:
        return aut[0]
    else:
        return None


def identificar_parcelas(texto):
    regex_parcelas = re.compile(r"(\d+) Parcelas", re.IGNORECASE)
    parcelas = regex_parcelas.findall(texto)
    if parcelas:
        return int(parcelas[0])
    else:
        return 1


def busca_valor(text):
    # Expressão regular para buscar por valores monetários
    regex_valor = re.compile(r"(?:R[Ss]?[$]?)\s*(\d{1,3}(?:[\.,]\d{3})*(?:,\d{2})?)")

    # Busca por valores monetários no texto
    valor_enviado_str = regex_valor.findall(text)

    # Converte a string do valor_enviado para float
    try:
        if valor_enviado_str:
            valor_str = valor_enviado_str[0].replace("R$ ", "").replace("RS ", "").replace(".", "").replace(",", ".")
            valor_enviado = float(valor_str)
        else:
            valor_enviado = None  # ou outra ação para tratar o erro

    except ValueError as e:
        valor_enviado = None  # ou outra ação para tratar o erro
        logging.error(f"Erro ao converter valor monetário: {e}", exc_info=True)
        return valor_enviado
    logging.info(f"Valor encontrado: {valor_enviado}")
    return valor_enviado


def search_cpnj(text):
    # Expressão regular para buscar o CNPJ
    regex_cnpj = re.compile(r"0?4[.,/]?930[.,/]?244[|/]?0136[.,/-]?17")

    # Busca pelo CNPJ no texto
    cnpj_encontrado = regex_cnpj.search(text)

    if cnpj_encontrado:
        cnpj_encontrado = True
    else:
        cnpj_encontrado = False
    return cnpj_encontrado


def search_id(text):
    # Expressão regular para buscar pelo ID da transação
    regex_id = re.compile(r"^[E£]\w{32}$", re.IGNORECASE)

    # Busca pelo ID da transação no texto
    id_transacao = regex_id.search(text)

    # Verifica se o ID da transação foi encontrado
    if id_transacao:
        id_transacao = id_transacao.group()
    else:
        id_transacao = "ID da transação não encontrado."
    return id_transacao


def search_datas(text):
    # Expressões regulares para diferentes formatos de data
    regex_data1 = r"\d{1,2}/\d{1,2}/\d{2,4}"  # formato dd/mm/aa ou dd/mm/aaaa
    regex_data2 = r"\d{1,2}\sde\s[a-z]+\sde\s\d{2,4}"  # formato dd de mês de aaaa
    regex_data3 = r"\d{1,2}\s[a-z]+\s\d{2,4}"  # formato dd mês aaaa
    regex_data4 = re.compile(r'\d{1,2}\s(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)\s\d{2}(?:\d{2})?',
                             flags=re.IGNORECASE)  # formato dd MÊS aaaa

    # Lista para armazenar as datas encontradas
    found_dates = []

    # Procura pelas datas no texto
    for regex in [regex_data1, regex_data2, regex_data3, regex_data4]:
        found_dates.extend(re.findall(regex, text.lower()))

    # Verifica se as datas encontradas são válidas
    for date in found_dates:
        try:
            if len(date) == 8:
                formato = '%d/%m/%y'  # Formato para ano com dois dígitos
            else:
                formato = '%d/%m/%Y'  # Formato para ano com quatro dígitos
            dt = datetime.strptime(date, formato)
            formated_dates = dt.strftime('%Y-%m-%d')  # Formato americano: YYYY-MM-DD
            return formated_dates
        except ValueError:
            pass

    return None


def check_user(bot, message):
    # Verifica se o usuário está cadastrado no banco de dados
    conn = mysql_connector()

    # Verifica se ocorreu um erro na conexão
    if isinstance(conn, mysql.connector.Error):
        # Trate o erro conforme necessário
        bot.send_message(message.chat.id, f"Ocorreu um erro ao verificar o usuário: {conn}")
        return False

    cursor = conn.cursor()

    telegram_id = message.from_user.id

    # Verifica se o usuário existe na tabela Usuario
    cursor.execute("SELECT telegram_id FROM Usuario WHERE telegram_id = %s", (telegram_id,))
    result = cursor.fetchone()

    # Fecha o cursor e a conexão
    cursor.close()
    conn.close()

    if result:
        # Usuário encontrado no banco de dados
        return True
    else:
        # Usuário não encontrado no banco de dados
        bot.send_message(telegram_id, f"Desculpe, você ainda não está cadastrado no sistema. Envie o código de verificação *{telegram_id}* ao administrador juntamente com o seu *Nome Completo*.")
        return False
