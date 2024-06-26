from PIL import Image
import requests
import logging
import pytesseract
import data_identify
import data_identify as d_i
import mysql.connector
import os
import shutil


def download_image(bot, telegram_token, message):
    # Obter o ID do arquivo da foto
    photo_message = message.photo[-1].file_id

    try:
        # Obter informações sobre o arquivo de imagem
        logging.info("Obtendo informações sobre o arquivo de image...")
        file_info = bot.get_file(photo_message)
        file_path = file_info.file_path

        # Fazer o download da image em sua resolução original
        logging.info("Fazendo download da image em sua resolução original...")
        response = requests.get(f"https://api.telegram.org/file/bot{telegram_token}/{file_path}")
        response.raise_for_status()

        # Verificar se a pasta 'imgs' existe e criá-la se necessário
        if not os.path.exists('imgs'):
            os.makedirs('imgs')

        path = "imgs/"

        # Salvar a imagem com maior resolução e qualidade
        path += f"{photo_message}.jpg"
        with open(path, "wb") as new_file, response:
            for chunk in response.iter_content(chunk_size=128):
                new_file.write(chunk)

        img = Image.open(path)

        # Salvar a imagem com 300dpi e 100% da qualidade
        img.save(path, dpi=(300, 300), quality=100)
        return img, path
    except Exception as e:
        bot.reply_to(message, "Erro ao baixar a imagem")
        logging.error(f"Erro ao baixar a imagem: {e}", exc_info=True)


def download_pdf(bot, telegram_token, message):
    # Obter o ID do arquivo do PDF
    pdf_message = message.document.file_id

    try:
        # Obter informações sobre o arquivo PDF
        logging.info("Obtendo informações sobre o arquivo PDF...")
        file_info = bot.get_file(pdf_message)
        file_path = file_info.file_path

        # Verificar se o arquivo é um PDF
        if not file_path.endswith('.pdf'):
            bot.reply_to(message, "O arquivo fornecido não é um PDF.")
            logging.warning("Arquivo fornecido não é um PDF.")
            return None

        # Fazer o download do PDF
        logging.info("Fazendo download do arquivo PDF...")
        response = requests.get(f"https://api.telegram.org/file/bot{telegram_token}/{file_path}")
        response.raise_for_status()

        # Verificar se a pasta 'pdfs' existe e criá-la se necessário
        if not os.path.exists('pdfs'):
            os.makedirs('pdfs')

        path = "pdfs/"

        # Salvar o arquivo PDF
        path += f"{pdf_message}.pdf"
        with open(path, "wb") as new_file:
            new_file.write(response.content)

        return path
    except Exception as e:
        bot.reply_to(message, "Erro ao baixar o arquivo PDF.")
        logging.error(f"Erro ao baixar o arquivo PDF: {e}", exc_info=True)
        return None


def save_data_to_database(cursor, telegram_id, message_id, texto, comprovante):
    try:
        # Crie a chave única
        chave = f"{telegram_id}_{message_id}"

        # Insira os dados gerais do comprovante na tabela de comprovantes
        query = "INSERT INTO comprovantes (chave, telegram_id, message_id, texto, comprovante) VALUES (%s, %s, %s, %s, %s)"
        values = (chave, telegram_id, message_id, texto, comprovante)
        cursor.execute(query, values)

        # Obtém o ID do último comprovante registrado
        query = "SELECT LAST_INSERT_ID()"
        cursor.execute(query)
        comprovante_id = cursor.fetchone()[0]

        # Verifica se há um comprovante registrado para o usuário
        if comprovante_id is None:
            return False, "Desculpe, nenhum comprovante registrado para esse usuário."

        # Salva as informações da transação na tabela apropriada
        if comprovante == "Cartão de Débito" or comprovante == "Cartão de Crédito":
            valor_transacao = d_i.busca_valor(texto)
            autorizacao = d_i.search_aut(texto)
            parcelas = d_i.identificar_parcelas(texto)
            data_transacao = d_i.search_datas(texto)
            cnpj_sels = d_i.search_cpnj(texto)

            # Verifica se todos os valores de transação estão presentes no texto
            if valor_transacao is None or autorizacao is None or parcelas is None or data_transacao is None or cnpj_sels is None:
                # Salva as informações incompletas na tabela de comprovantes incompletos de cartão
                query = "INSERT INTO comprovantes_incompletos_cartao (comprovante_id, valor_enviado, data_transacao, cnpj_sels, autorizacao, parcelas) VALUES (%s, %s, %s, %s, %s, %s)"
                values = (
                    comprovante_id, valor_transacao, data_transacao, cnpj_sels, autorizacao, parcelas
                )
                cursor.execute(query, values)
                return False, "Não foi possível identificar todas as informações do comprovante automaticamente. Encaminhamos seu comprovante para um atendente, que irá verificar e processar manualmente. Obrigado pela compreensão!"

            query = "INSERT INTO comprovantes_cartao (comprovante_id, valor_enviado, data_transacao, cnpj_sels, autorizacao, parcelas) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (
                comprovante_id, valor_transacao, data_transacao, cnpj_sels, autorizacao, parcelas
            )
            cursor.execute(query, values)

        elif comprovante == "Transferência Pix":
            valor_transacao = d_i.busca_valor(texto)
            id_transacao = d_i.search_id(texto)
            data_transacao = d_i.search_datas(texto)
            cnpj_sels = d_i.search_cpnj(texto)

            # Verifica se todos os valores de transação estão presentes no texto
            if valor_transacao is None or id_transacao is None or data_transacao is None or cnpj_sels is None:
                # Salva as informações incompletas na tabela de comprovantes incompletos de Pix
                query = "INSERT INTO comprovantes_incompletos_pix (comprovante_id, valor_enviado, data_transacao, cnpj_sels, id_transacao) VALUES (%s, %s, %s, %s, %s)"
                values = (
                    comprovante_id, valor_transacao, data_transacao, cnpj_sels, id_transacao
                )
                cursor.execute(query, values)
                return False, "Não foi possível identificar todas as informações do comprovante automaticamente. Encaminhamos seu comprovante para um atendente, que irá verificar e processar manualmente. Obrigado pela compreensão!"

            query = "INSERT INTO comprovantes_pix (comprovante_id, valor_enviado, data_transacao, cnpj_sels, id_transacao) VALUES (%s, %s, %s, %s, %s)"
            values = (
                comprovante_id, valor_transacao, data_transacao, cnpj_sels, id_transacao
            )
            cursor.execute(query, values)

        return True, "Comprovante registrado com sucesso."

    except Exception as e:
        return False, f"Erro ao salvar o comprovante: {str(e)}"


def photo_process(bot, telegram_token, message):
    # Configurações do Tesseract
    pytesseract.pytesseract.tesseract_cmd = r'D:\\tesseract-ORC\\tesseract.exe'
    custom_config = r'--oem 3 --psm 6 -l por'

    try:
        conn = d_i.mysql_connector()

        # Verifica se ocorreu um erro na conexão
        if isinstance(conn, mysql.connector.Error):
            bot.send_message(message.chat.id, f"Ocorreu um erro ao processar a foto: {conn}")
            return

        cursor = conn.cursor()

        img, path = download_image(bot, telegram_token, message)

        # Extraí o texto da imagem
        logging.info("Extraindo texto da imagem com o pytesseract...")
        texto = pytesseract.image_to_string(img, config=custom_config)
        logging.debug(f"Texto extraído da imagem: {texto}")

        comprovante = d_i.diferenciar_comprovante(texto, message, bot)

        success, response = save_data_to_database(cursor, message.chat.id, message.message_id, texto, comprovante)

        if success:
            conn.commit()
            bot.send_message(message.chat.id, text=response)
        else:
            conn.commit()
            # Verificar se a pasta 'review' existe e criá-la se necessário
            if not os.path.exists('review'):
                os.makedirs('review')

            # Mover o arquivo para a pasta de revisão
            review_path = f"review/{message.chat.id}_{message.message_id}.jpg"
            shutil.move(path, review_path)
            bot.send_message(message.chat.id, text=response)

        # Fecha o cursor e a conexão
        cursor.close()
        conn.close()

    except Exception as e:
        bot.reply_to(message, "Erro ao processar a imagem")
        logging.error(f"Erro ao processar a imagem: {e}", exc_info=True)


def document_process(bot, telegram_token, message):
    try:
        conn = d_i.mysql_connector()

        # Verifica se ocorreu um erro na conexão
        if isinstance(conn, mysql.connector.Error):
            # Trate o erro conforme necessário
            bot.send_message(message.chat.id, f"Ocorreu um erro ao processar o documento: {conn}")
            return

        cursor = conn.cursor()

        path = download_pdf(bot, telegram_token, message)

        # Lê o texto no PDF
        logging.info("Extraindo texto do PDF...")
        texto = d_i.read_pdf(path)
        logging.debug(f"Texto extraído do PDF: {texto}")

        comprovante = d_i.diferenciar_comprovante(texto, message, bot)

        # Salva os dados no banco de dados
        success, response = save_data_to_database(cursor, message.chat.id, message.message_id, texto, comprovante)
        if success:
            conn.commit()
            logging.info("Dados salvos no banco de dados com sucesso.")
            bot.send_message(message.chat.id, text=response)
        else:
            conn.commit()

            # Verificar se a pasta 'review' existe e criá-la se necessário
            if not os.path.exists('review'):
                os.makedirs('review')

            # Mover o arquivo para a pasta de revisão
            review_path = f"review/{message.chat.id}_{message.message_id}.jpg"
            shutil.move(path, review_path)
            bot.send_message(message.chat.id, text=response)

            logging.error(f"Erro ao salvar os dados: {response}")

            # Verificar se a pasta 'review' existe e criá-la se necessário
            if not os.path.exists('review'):
                os.makedirs('review')

            # Mover o arquivo para a pasta de revisão
            review_path = f"review/{message.chat.id}_{message.message_id}.pdf"
            shutil.move(path, review_path)
            bot.send_message(message.chat.id, text=response)

        # Fecha o cursor e a conexão
        cursor.close()
        conn.close()

    except Exception as e:
        logging.error(f"Erro ao processar o documento: {str(e)}")


def enviar_atualizacao(bot):
    novo_comando = '/saldo'
    id_usuario = ""

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


def get_common_params():
    return {
        "isExcel": "false",
        "isCsv": "false",
        "isAnalytical": "true",
        "minimizedDataReport": "false",
        "campaignType": "10",
        "access_token": "aa90aa5b2706cd1ade024e2dd7daa98a",
        "DenominationalEntityId": "c10dd043-e46d-e511-bbf3-002590396224"
    }


def get_params_colporteur(bot, message):
    # Crie um cursor para executar as consultas
    conn = d_i.mysql_connector()

    # Verifica se ocorreu um erro na conexão
    if isinstance(conn, mysql.connector.Error):
        # Trate o erro conforme necessário
        bot.send_message(message.chat.id, f"Ocorreu um erro ao obter os parâmetros do colportor: {conn}")
        return

    cursor = conn.cursor()

    # Faz a consulta no banco de dados para obter as informações do usuário
    try:
        # Execute a consulta SQL para obter as informações do usuário
        query = f'SELECT isColporteur, colporteur_id FROM Usuario WHERE telegram_id = {message.from_user.id}'
        cursor.execute(query)
        result = cursor.fetchone()

        # Verifique se o usuário é um colportor e obtenha as informações necessárias
        if result[0]:
            query = f"SELECT team_campaign_id FROM Colporteur WHERE colporteur_id = '{result[1]}'"

            cursor.execute(query)

            team_campaign_id = cursor.fetchone()[0]

            params = get_common_params()
            params["teamCampaignColporteurId"] = result[1]
            params["teamCampaignId"] = team_campaign_id

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


def get_all_params_colporteur(bot, message):
    # Busca os dados dos colportores no banco de dados
    colporteur_ids, colporteur_names = get_all_colporteur_ids()

    params_list = []

    # Crie um cursor para executar as consultas
    conn = d_i.mysql_connector()

    # Verifica se ocorreu um erro na conexão
    if isinstance(conn, mysql.connector.Error):
        # Trate o erro conforme necessário
        bot.send_message(message.chat.id, f"Ocorreu um erro ao obter os parâmetros dos colportores: {conn}")
        return params_list

    cursor = conn.cursor()

    # Faz a consulta no banco de dados para obter as informações dos colportores
    try:
        for colporteur_id in colporteur_ids:
            query = f"SELECT team_campaign_id FROM Colporteur WHERE colporteur_id = '{colporteur_id}'"
            cursor.execute(query)
            result = cursor.fetchone()

            team_campaign_id = result[0]

            params = get_common_params()
            params["teamCampaignColporteurId"] = colporteur_id
            params["teamCampaignId"] = team_campaign_id

            params_list.append(params)

    except mysql.connector.Error as error:
        # Se ocorrer algum erro ao conectar ao banco de dados, envie uma mensagem de erro
        bot.send_message(message.chat.id, f"Ocorreu um erro ao obter as informações dos colportores: {error}")
    finally:
        # Sempre feche o cursor e a conexão após a consulta
        cursor.close()
        conn.close()

    return params_list, colporteur_names


def get_all_colporteur_ids():
    conn = data_identify.mysql_connector()
    cursor = conn.cursor()

    # Executa a consulta para obter os IDs e nomes dos colportores
    cursor.execute('SELECT colporteur_id, colporteur_name FROM colporteur')
    result = cursor.fetchall()

    # Extrai os IDs e nomes dos resultados da consulta
    colporteur_ids = [row[0] for row in result]
    colporteur_names = [row[1] for row in result]

    conn.close()

    return colporteur_ids, colporteur_names
