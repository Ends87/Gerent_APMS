CREATE DATABASE IF NOT EXISTS test_bot_telegram;

USE test_bot_telegram;

CREATE TABLE IF NOT EXISTS team_campaign (
  team_campaign_id  VARCHAR(36) NOT NULL,
  campaign_name VARCHAR(255) NOT NULL,
  PRIMARY KEY (team_campaign_id)
);

CREATE TABLE IF NOT EXISTS Colporteur (
  colporteur_id  VARCHAR(36) NOT NULL,
  colporteur_name VARCHAR(255) NOT NULL,
  team_campaign_id VARCHAR(36) NOT NULL,
  FOREIGN KEY (team_campaign_id) REFERENCES team_campaign(team_campaign_id),
  PRIMARY KEY (colporteur_id)
);

CREATE TABLE IF NOT EXISTS Usuario (
  telegram_id bigint NOT NULL,
  name VARCHAR(255) NOT NULL,
  isColporteur BOOLEAN NOT NULL,
  colporteur_id VARCHAR(36),
  FOREIGN KEY (colporteur_id) REFERENCES Colporteur(colporteur_id),
  PRIMARY KEY (telegram_id),
  CHECK (isColporteur = TRUE AND colporteur_id IS NOT NULL OR isColporteur = FALSE)
);

CREATE TABLE IF NOT EXISTS comprovantes (
    comprovante_id INT AUTO_INCREMENT PRIMARY KEY,
    chave VARCHAR(255) NOT NULL,
    telegram_id BIGINT NOT NULL,
    message_id INT NOT NULL,
    texto TEXT NOT NULL,
    comprovante VARCHAR(255) NOT NULL,
    FOREIGN KEY (telegram_id) REFERENCES usuario(telegram_id)
);

CREATE TABLE IF NOT EXISTS comprovantes_pix (
    comprovante_id INT PRIMARY KEY,
    valor_enviado DECIMAL(10, 2) NOT NULL,
    data_transacao DATE NOT NULL,
    cnpj_sels BOOLEAN NOT NULL,
    id_transacao VARCHAR(255) NOT NULL,
    FOREIGN KEY (comprovante_id) REFERENCES comprovantes(comprovante_id)
);

CREATE TABLE IF NOT EXISTS comprovantes_cartao (
    comprovante_id INT PRIMARY KEY,
    valor_enviado DECIMAL(10, 2) NOT NULL,
    data_transacao DATE NOT NULL,
    cnpj_sels BOOLEAN NOT NULL,
    autorizacao VARCHAR(255) NOT NULL,
    parcelas INT NOT NULL,
    FOREIGN KEY (comprovante_id) REFERENCES comprovantes(comprovante_id)
);

CREATE TABLE IF NOT EXISTS comprovantes_incompletos_pix (
    comprovante_id INT PRIMARY KEY,
    valor_enviado DECIMAL(10, 2),
    data_transacao DATE,
    cnpj_sels BOOLEAN,
    id_transacao VARCHAR(255),
    FOREIGN KEY (comprovante_id) REFERENCES comprovantes(comprovante_id)
);

CREATE TABLE IF NOT EXISTS comprovantes_incompletos_cartao (
    comprovante_id INT PRIMARY KEY,
    valor_enviado DECIMAL(10, 2),
    data_transacao DATE,
    cnpj_sels BOOLEAN,
    autorizacao VARCHAR(255),
    parcelas INT,
    FOREIGN KEY (comprovante_id) REFERENCES comprovantes(comprovante_id)
);

CREATE TABLE IF NOT EXISTS Respostas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    tempo_oracao INT,
    horas_trabalho TIME,
    quantidade_visitas INT,
    valor_vendas DECIMAL(10, 2),
    material_vendido VARCHAR(255),
    data_resposta DATE,
    FOREIGN KEY (user_id) REFERENCES Usuario (telegram_id)
);

INSERT INTO team_campaign (team_campaign_id, campaign_name) VALUES ('1', 'Dev');

INSERT INTO Colporteur (colporteur_id, colporteur_name, team_campaign_id) VALUES ('1', 'Ends', '1');

INSERT INTO Usuario (telegram_id, name, isColporteur, colporteur_id)
VALUES (803998885, 'Ends', false, '1');
