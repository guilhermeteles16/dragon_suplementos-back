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


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

NOME_BANCO = "loja_suplementos.db"


# ============================================================================
# CONEXÃO COM O BANCO
# ============================================================================

def obter_conexao():
    """
    Cria e retorna uma conexão com o banco de dados SQLite.
    Ativa o suporte a chaves estrangeiras.
    """

    conexao = sqlite3.connect(NOME_BANCO)

    conexao.execute(
        "PRAGMA foreign_keys = ON"
    )

    conexao.row_factory = sqlite3.Row

    return conexao


# ============================================================================
# CRIAÇÃO DAS TABELAS
# ============================================================================

def criar_tabelas(conexao):
    """
    Cria todas as tabelas do sistema, caso ainda não existam.
    """

    cursor = conexao.cursor()


    # ------------------------------------------------------------------------
    # TABELA DE CATEGORIAS
    # ------------------------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)


    # ------------------------------------------------------------------------
    # TABELA DE PRODUTOS
    # ------------------------------------------------------------------------

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

            FOREIGN KEY (categoria_id)
                REFERENCES categorias (id)
                ON DELETE SET NULL
        )
    """)


    # ------------------------------------------------------------------------
    # CORREÇÃO PARA BANCOS ANTIGOS
    # ------------------------------------------------------------------------
    # Se o banco já existia antes da criação da coluna estoque,
    # CREATE TABLE IF NOT EXISTS não altera a tabela antiga.
    #
    # Por isso verificamos se a coluna existe e adicionamos caso necessário.

    colunas_produtos = cursor.execute(
        "PRAGMA table_info(produtos)"
    ).fetchall()

    nomes_colunas = [
        coluna["name"]
        for coluna in colunas_produtos
    ]

    if "estoque" not in nomes_colunas:

        cursor.execute("""
            ALTER TABLE produtos
            ADD COLUMN estoque INTEGER NOT NULL DEFAULT 0
        """)

        print(
            "Coluna 'estoque' adicionada à tabela produtos."
        )


    # ------------------------------------------------------------------------
    # TABELA DE USUÁRIOS
    # ------------------------------------------------------------------------

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


    # ------------------------------------------------------------------------
    # TABELA DO CARRINHO
    # ------------------------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carrinho_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL CHECK (quantidade > 0),

            FOREIGN KEY (usuario_id)
                REFERENCES usuarios (id)
                ON DELETE CASCADE,

            FOREIGN KEY (produto_id)
                REFERENCES produtos (id)
                ON DELETE CASCADE,

            UNIQUE (usuario_id, produto_id)
        )
    """)


    conexao.commit()


# ============================================================================
# CATEGORIAS INICIAIS
# ============================================================================

def inserir_categorias_iniciais(conexao):
    """
    Garante que as categorias utilizadas pelo sistema existam no banco.

    As categorias são:

        - suplementos
        - roupas
        - acessorios
        - equipamentos

    INSERT OR IGNORE evita duplicar categorias que já existem.
    """

    cursor = conexao.cursor()


    categorias_iniciais = [
        ("suplementos",),
        ("roupas",),
        ("acessorios",),
        ("equipamentos",),
    ]


    cursor.executemany(
        """
        INSERT OR IGNORE INTO categorias (nome)
        VALUES (?)
        """,
        categorias_iniciais
    )


    conexao.commit()


    print(
        "Categorias verificadas com sucesso."
    )


# ============================================================================
# INICIALIZAÇÃO DO BANCO
# ============================================================================

def inicializar_banco():
    """
    Inicializa o banco de dados.

    Cria o banco caso ele não exista,
    cria as tabelas necessárias,
    corrige estruturas antigas
    e garante as categorias iniciais.
    """

    banco_ja_existia = os.path.exists(
        NOME_BANCO
    )


    conexao = obter_conexao()


    criar_tabelas(
        conexao
    )


    inserir_categorias_iniciais(
        conexao
    )


    conexao.close()


    if not banco_ja_existia:

        print(
            f"Banco de dados '{NOME_BANCO}' criado com sucesso."
        )

    else:

        print(
            f"Banco de dados '{NOME_BANCO}' "
            "verificado/atualizado com sucesso."
        )


# ============================================================================
# EXECUÇÃO DIRETA
# ============================================================================

if __name__ == "__main__":

    inicializar_banco()

    print(
        "Processo finalizado."
    )