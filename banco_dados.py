# -*- coding: utf-8 -*-
"""
banco_dados.py

Este arquivo é responsável por criar e configurar o banco de dados SQLite
do projeto Dragon Suplementos.

Ele cria o arquivo 'loja_suplementos.db' (caso não exista) e cria todas
as tabelas necessárias para o funcionamento da API:

    - categorias
    - produtos
    - usuarios
    - carrinho_itens

Pode ser executado diretamente:

    python banco_dados.py

Ou importado pelo app.py, que chama a função inicializar_banco()
automaticamente ao iniciar o servidor.
"""

import sqlite3
import os

# Nome do arquivo do banco de dados SQLite
NOME_BANCO = "loja_suplementos.db"


def obter_conexao():
    """
    Cria e retorna uma conexão com o banco de dados SQLite.
    Ativa o suporte a chaves estrangeiras (foreign keys), que o SQLite
    não ativa por padrão.
    """
    conexao = sqlite3.connect(NOME_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
    return conexao


def criar_tabelas(conexao):
    """
    Cria todas as tabelas do sistema, caso ainda não existam.
    """
    cursor = conexao.cursor()

    # Tabela de categorias de produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)

    # Tabela de produtos
    # categoria_id pode ficar NULL se a categoria for excluída
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            imagem TEXT,
            descricao TEXT,
            preco REAL NOT NULL CHECK (preco >= 0),
            estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
            categoria_id INTEGER,
            data_cadastro TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
                ON DELETE SET NULL
        )
    """)

    # Tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telefone TEXT NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            data_nascimento TEXT NOT NULL,
            categoria TEXT NOT NULL,
            senha_hash TEXT NOT NULL,
            data_cadastro TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # Tabela de itens do carrinho
    # Um usuário não pode ter duas linhas do mesmo produto (UNIQUE composta)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carrinho_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL CHECK (quantidade > 0),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
                ON DELETE CASCADE,
            UNIQUE (usuario_id, produto_id)
        )
    """)

    conexao.commit()


def inserir_categorias_iniciais(conexao):
    """
    Insere algumas categorias iniciais, apenas se a tabela estiver vazia.
    Isso evita duplicar categorias toda vez que o servidor iniciar.
    """
    cursor = conexao.cursor()
    cursor.execute("SELECT COUNT(*) FROM categorias")
    total = cursor.fetchone()[0]

    if total == 0:
        categorias_iniciais = [
            ("Whey Protein",),
            ("Creatina",),
            ("Pré-Treino",),
            ("Vitaminas",),
            ("Acessórios",),
        ]
        cursor.executemany(
            "INSERT INTO categorias (nome) VALUES (?)",
            categorias_iniciais
        )
        conexao.commit()
        print("Categorias iniciais inseridas com sucesso.")


def inicializar_banco():
    """
    Função principal de inicialização do banco de dados.
    Cria o banco (se não existir), cria as tabelas e insere os dados
    iniciais de categorias.

    Essa função é chamada automaticamente pelo app.py ao iniciar o
    servidor, então não é obrigatório executar este arquivo manualmente.
    """
    banco_ja_existia = os.path.exists(NOME_BANCO)

    conexao = obter_conexao()
    criar_tabelas(conexao)
    inserir_categorias_iniciais(conexao)
    conexao.close()

    if not banco_ja_existia:
        print(f"Banco de dados '{NOME_BANCO}' criado com sucesso.")
    else:
        print(f"Banco de dados '{NOME_BANCO}' verificado/atualizado com sucesso.")


# Permite executar este arquivo diretamente: python banco_dados.py
if __name__ == "__main__":
    inicializar_banco()
    print("Processo finalizado.")
