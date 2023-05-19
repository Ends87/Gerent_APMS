import os
import logging
import re
from datetime import datetime
import json
from unidecode import unidecode
import PyPDF2


def read_pdf(path):
    text = ""
    with open(path, 'rb') as f:
        reader_pdf = PyPDF2.PdfReader(f)
        num_pages = len(reader_pdf.pages)
        for page in range(num_pages):
            page_content = reader_pdf.pages[page]
            text += page_content.extract_text()
    return text


def diferenciar_comprovante(texto, message, bot):
    texto = unidecode(texto.lower())
    if "pix" in texto or "99Pay" in texto:
        logging.info("Comprovante de Transferência Pix")
        bot.reply_to(message, "Comprovante de Transferência Pix")
        return "Transferência Pix"
    elif "parcelado" in texto:
        logging.info("Comprovante de Cartão de Crédito")
        bot.reply_to(message, "Comprovante de Cartão de Crédito")
        return "Cartão de Crédito"
    elif "debito a vista" in texto:
        logging.info("Comprovante de Cartão de Débito")
        bot.reply_to(message, "Comprovante de Cartão de Débito")
        return "Cartão de Débito"
    else:
        logging.warning("Não foi possível diferenciar o comprovante")
        bot.reply_to(message, "Não foi possível diferenciar o comprovante")
        return "Não foi possível diferenciar o comprovante"


def buscar_aut(texto):
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


def busca_valor(texto):
    # Expressão regular para buscar por valores monetários
    regex_valor = re.compile(r"(?:R[Ss]?[$]?)\s*(\d{1,3}(?:[\.,]\d{3})*(?:,\d{2})?)")

    # Busca por valores monetários no texto
    valor_enviado_str = regex_valor.findall(texto)

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


def busca_cpnj(texto):
    # Expressão regular para buscar o CNPJ
    regex_cnpj = re.compile(r"0?4[.,/]?930[.,/]?244[|/]?0136[.,/-]?17")

    # Busca pelo CNPJ no texto
    cnpj_encontrado = regex_cnpj.search(texto)

    if cnpj_encontrado:
        cnpj_encontrado = True
    else:
        cnpj_encontrado = False
    return cnpj_encontrado


def busca_ID(texto):
    # Expressão regular para buscar pelo ID da transação
    regex_id = re.compile(r"^[E£]\w{32}$", re.IGNORECASE)

    # Busca pelo ID da transação no texto
    id_transacao = regex_id.search(texto)

    # Verifica se o ID da transação foi encontrado
    if id_transacao:
        id_transacao = id_transacao.group()
    else:
        id_transacao = "ID da transação não encontrado."
    return id_transacao


def buscar_datas(texto):
    # Expressões regulares para diferentes formatos de data
    regex_data1 = r"\d{1,2}/\d{1,2}/\d{2,4}"  # formato dd/mm/aa ou dd/mm/aaaa
    regex_data2 = r"\d{1,2}\sde\s[a-z]+\sde\s\d{2,4}"  # formato dd de mês de aaaa
    regex_data3 = r"\d{1,2}\s[a-z]+\s\d{2,4}"  # formato dd mês aaaa
    regex_data4 = re.compile(r'\d{1,2}\s(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)\s\d{2}(?:\d{2})?',
                             flags=re.IGNORECASE)  # formato dd MÊS aaaa

    # Lista para armazenar as datas encontradas
    datas_encontradas = []

    # Procura pelas datas no texto
    for regex in [regex_data1, regex_data2, regex_data3, regex_data4]:
        datas_encontradas.extend(re.findall(regex, texto.lower()))

    # Verifica se as datas encontradas são válidas
    for data in datas_encontradas:
        try:
            if len(data) == 8:
                formato = '%d/%m/%y'  # Formato para ano com dois dígitos
            else:
                formato = '%d/%m/%Y'  # Formato para ano com quatro dígitos
            dt = datetime.strptime(data, formato)
            data_formatada = dt.strftime('%Y-%m-%d')  # Formato americano: YYYY-MM-DD
            return data_formatada
        except ValueError:
            pass

    return None


def verificar_usuario(bot, message):
    dados_usuarios_dir = 'dados_usuarios'
    solicitacoes_file = 'solicitacoes.json'

    user_id = message.from_user.id
    user_id_str = str(user_id)

    # Verifica se existe um arquivo JSON com o ID do usuário
    if not os.path.exists(os.path.join(dados_usuarios_dir, f'{user_id_str}.json')):
        # Caso não exista, envia mensagem solicitando que entre em contato com o administrador
        bot.send_message(user_id, f"Desculpe, você ainda não está cadastrado no sistema. Envie o código de verificação *{user_id}* ao administrador juntamente com o seu *Nome Completo*.")

        # Armazena o ID do usuário e o nome completo informado em um arquivo de solicitações
        with open(os.path.join(dados_usuarios_dir, solicitacoes_file), 'a') as f:
            json.dump({'id': user_id_str, 'nome': message.from_user.full_name}, f)
            f.write('\n')

        return False

    # Caso exista, o usuário já está cadastrado
    return True
