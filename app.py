# -*- coding: utf-8 -*-
"""
app.py

API do projeto Dragon Suplementos.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import sqlite3
import os

from banco_dados import obter_conexao, inicializar_banco


# ============================================================================
# CONFIGURAÇÃO INICIAL
# ============================================================================

app = Flask(__name__)

CORS(app)

# Pasta onde as imagens dos produtos serão armazenadas
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Inicializa o banco
inicializar_banco()


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def resposta_erro(mensagem, status=400):
    return jsonify({"erro": mensagem}), status


def produto_para_dict(linha):
    return {
        "id": linha["id"],
        "nome": linha["nome"],
        "imagem": linha["imagem"],
        "descricao": linha["descricao"],
        "preco": linha["preco"],
        "estoque": linha["estoque"],
        "categoria_id": linha["categoria_id"],
        "categoria": linha["categoria_nome"],
        "data_cadastro": linha["data_cadastro"],
    }


def usuario_para_dict(linha):
    return {
        "id": linha["id"],
        "nome": linha["nome"],
        "email": linha["email"],
        "telefone": linha["telefone"],
        "cpf": linha["cpf"],
        "data_nascimento": linha["data_nascimento"],
        "categoria": linha["categoria"],
        "data_cadastro": linha["data_cadastro"],
    }


# ============================================================================
# TRATAMENTO DE ERROS
# ============================================================================

@app.errorhandler(404)
def erro_404(e):
    return resposta_erro("Rota não encontrada", 404)


@app.errorhandler(405)
def erro_405(e):
    return resposta_erro("Método não permitido para esta rota", 405)


@app.errorhandler(500)
def erro_500(e):
    return resposta_erro("Erro interno do servidor", 500)


# ============================================================================
# ROTA INICIAL
# ============================================================================

@app.route("/", methods=["GET"])
def rota_inicial():
    return jsonify({
        "nome": "Dragon Suplementos API",
        "status": "online",
        "mensagem": "Back-end funcionando!"
    })


# ============================================================================
# IMAGENS DOS PRODUTOS
# ============================================================================

@app.route("/uploads/<filename>")
def servir_imagem(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ============================================================================
# API DE PRODUTOS
# ============================================================================

# LISTAR PRODUTOS
@app.route("/api/produtos", methods=["GET"])
def listar_produtos():

    conexao = obter_conexao()

    linhas = conexao.execute("""
        SELECT
            p.id,
            p.nome,
            p.imagem,
            p.descricao,
            p.preco,
            p.estoque,
            p.categoria_id,
            p.data_cadastro,
            c.nome AS categoria_nome
        FROM produtos p
        LEFT JOIN categorias c
            ON p.categoria_id = c.id
        ORDER BY p.id
    """).fetchall()

    conexao.close()

    produtos = [
        produto_para_dict(linha)
        for linha in linhas
    ]

    return jsonify(produtos)


# OBTER PRODUTO
@app.route("/api/produtos/<int:produto_id>", methods=["GET"])
def obter_produto(produto_id):

    conexao = obter_conexao()

    linha = conexao.execute("""
        SELECT
            p.id,
            p.nome,
            p.imagem,
            p.descricao,
            p.preco,
            p.estoque,
            p.categoria_id,
            p.data_cadastro,
            c.nome AS categoria_nome
        FROM produtos p
        LEFT JOIN categorias c
            ON p.categoria_id = c.id
        WHERE p.id = ?
    """, (produto_id,)).fetchone()

    conexao.close()

    if linha is None:
        return resposta_erro(
            "Produto não encontrado",
            404
        )

    return jsonify(produto_para_dict(linha))


# CADASTRAR PRODUTO
@app.route("/api/produtos", methods=["POST"])
def criar_produto():

    # ------------------------------------------------------------------------
    # Receber dados do formulário
    # ------------------------------------------------------------------------

    nome = request.form.get("nome")
    categoria = request.form.get("categoria")
    descricao = request.form.get("descricao")
    preco = request.form.get("preco")
    estoque = request.form.get("estoque")

    imagem = request.files.get("imagem")


    # ------------------------------------------------------------------------
    # Validações
    # ------------------------------------------------------------------------

    if not nome:
        return resposta_erro(
            "O campo 'nome' é obrigatório"
        )

    if not categoria:
        return resposta_erro(
            "O campo 'categoria' é obrigatório"
        )

    if preco is None:
        return resposta_erro(
            "O campo 'preco' é obrigatório"
        )

    if estoque is None:
        return resposta_erro(
            "O campo 'estoque' é obrigatório"
        )


    # ------------------------------------------------------------------------
    # Validar preço
    # ------------------------------------------------------------------------

    try:
        preco = float(preco)

    except (ValueError, TypeError):
        return resposta_erro(
            "O campo 'preco' deve ser um número"
        )

    if preco < 0:
        return resposta_erro(
            "O preço não pode ser negativo"
        )


    # ------------------------------------------------------------------------
    # Validar estoque
    # ------------------------------------------------------------------------

    try:
        estoque = int(estoque)

    except (ValueError, TypeError):
        return resposta_erro(
            "O campo 'estoque' deve ser um número inteiro"
        )

    if estoque < 0:
        return resposta_erro(
            "O estoque não pode ser negativo"
        )


    # ------------------------------------------------------------------------
    # Validar imagem
    # ------------------------------------------------------------------------

    if imagem is None:
        return resposta_erro(
            "A imagem é obrigatória"
        )

    if imagem.filename == "":
        return resposta_erro(
            "Nome da imagem inválido"
        )


    # ------------------------------------------------------------------------
    # Abrir conexão
    # ------------------------------------------------------------------------

    conexao = obter_conexao()


    # ------------------------------------------------------------------------
    # Encontrar categoria
    # ------------------------------------------------------------------------

    categoria_linha = conexao.execute("""
        SELECT id, nome
        FROM categorias
        WHERE LOWER(nome) = LOWER(?)
    """, (
        categoria.strip(),
    )).fetchone()


    if categoria_linha is None:

        conexao.close()

        return resposta_erro(
            "A categoria informada não existe"
        )


    categoria_id = categoria_linha["id"]


    # ------------------------------------------------------------------------
    # Salvar imagem
    # ------------------------------------------------------------------------

    nome_arquivo = secure_filename(
        imagem.filename
    )

    caminho_arquivo = os.path.join(
        UPLOAD_FOLDER,
        nome_arquivo
    )

    imagem.save(caminho_arquivo)


    # URL da imagem
    caminho_imagem = (
        f"https://dragon-suplementos-back-end.onrender.com/uploads/{nome_arquivo}"
    )


    # ------------------------------------------------------------------------
    # Salvar produto no banco
    # ------------------------------------------------------------------------

    cursor = conexao.execute("""
        INSERT INTO produtos
        (
            nome,
            imagem,
            descricao,
            preco,
            estoque,
            categoria_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        nome,
        caminho_imagem,
        descricao,
        preco,
        estoque,
        categoria_id
    ))


    conexao.commit()

    novo_id = cursor.lastrowid


    # ------------------------------------------------------------------------
    # Buscar produto recém-criado
    # ------------------------------------------------------------------------

    linha = conexao.execute("""
        SELECT
            p.id,
            p.nome,
            p.imagem,
            p.descricao,
            p.preco,
            p.estoque,
            p.categoria_id,
            p.data_cadastro,
            c.nome AS categoria_nome
        FROM produtos p
        LEFT JOIN categorias c
            ON p.categoria_id = c.id
        WHERE p.id = ?
    """, (
        novo_id,
    )).fetchone()


    conexao.close()


    # ------------------------------------------------------------------------
    # Retornar produto criado
    # ------------------------------------------------------------------------

    return jsonify(
        produto_para_dict(linha)
    ), 201
    
    
# ATUALIZAR PRODUTO
@app.route("/api/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto(produto_id):

    dados = request.get_json(
        silent=True
    ) or {}

    conexao = obter_conexao()

    produto_existente = conexao.execute(
        """
        SELECT *
        FROM produtos
        WHERE id = ?
        """,
        (produto_id,)
    ).fetchone()

    if produto_existente is None:

        conexao.close()

        return resposta_erro(
            "Produto não encontrado",
            404
        )

    nome = dados.get(
        "nome",
        produto_existente["nome"]
    )

    imagem = dados.get(
        "imagem",
        produto_existente["imagem"]
    )

    descricao = dados.get(
        "descricao",
        produto_existente["descricao"]
    )

    preco = dados.get(
        "preco",
        produto_existente["preco"]
    )

    categoria_id = dados.get(
        "categoria_id",
        produto_existente["categoria_id"]
    )


    if not nome:

        conexao.close()

        return resposta_erro(
            "O campo 'nome' não pode ficar vazio"
        )


    try:
        preco = float(preco)

    except (ValueError, TypeError):

        conexao.close()

        return resposta_erro(
            "O campo 'preco' deve ser um número"
        )


    if preco < 0:

        conexao.close()

        return resposta_erro(
            "O preço não pode ser negativo"
        )


    if categoria_id is not None:

        categoria = conexao.execute(
            """
            SELECT id
            FROM categorias
            WHERE id = ?
            """,
            (categoria_id,)
        ).fetchone()

        if categoria is None:

            conexao.close()

            return resposta_erro(
                "Categoria informada não existe"
            )


    conexao.execute("""
        UPDATE produtos
        SET
            nome = ?,
            imagem = ?,
            descricao = ?,
            preco = ?,
            categoria_id = ?
        WHERE id = ?
    """, (
        nome,
        imagem,
        descricao,
        preco,
        categoria_id,
        produto_id
    ))

    conexao.commit()


    linha = conexao.execute("""
        SELECT
            p.id,
            p.nome,
            p.imagem,
            p.descricao,
            p.preco,
            p.estoque,
            p.categoria_id,
            p.data_cadastro,
            c.nome AS categoria_nome
        FROM produtos p
        LEFT JOIN categorias c
            ON p.categoria_id = c.id
        WHERE p.id = ?
    """, (produto_id,)).fetchone()

    conexao.close()

    return jsonify(
        produto_para_dict(linha)
    )


# EXCLUIR PRODUTO
@app.route("/api/produtos/<int:produto_id>", methods=["DELETE"])
def excluir_produto(produto_id):

    conexao = obter_conexao()

    produto_existente = conexao.execute(
        """
        SELECT id
        FROM produtos
        WHERE id = ?
        """,
        (produto_id,)
    ).fetchone()

    if produto_existente is None:

        conexao.close()

        return resposta_erro(
            "Produto não encontrado",
            404
        )

    conexao.execute(
        """
        DELETE FROM produtos
        WHERE id = ?
        """,
        (produto_id,)
    )

    conexao.commit()
    conexao.close()

    return jsonify({
        "mensagem": "Produto excluído com sucesso"
    })


# ============================================================================
# API DE CATEGORIAS
# ============================================================================

@app.route("/api/categorias", methods=["GET"])
def listar_categorias():

    conexao = obter_conexao()

    linhas = conexao.execute(
        """
        SELECT id, nome
        FROM categorias
        ORDER BY nome
        """
    ).fetchall()

    conexao.close()

    categorias = [
        {
            "id": linha["id"],
            "nome": linha["nome"]
        }
        for linha in linhas
    ]

    return jsonify(categorias)


@app.route("/api/categorias", methods=["POST"])
def criar_categoria():

    dados = request.get_json(
        silent=True
    ) or {}

    nome = dados.get("nome")

    if not nome:
        return resposta_erro(
            "O campo 'nome' é obrigatório"
        )

    conexao = obter_conexao()

    existente = conexao.execute(
        """
        SELECT id
        FROM categorias
        WHERE nome = ?
        """,
        (nome,)
    ).fetchone()

    if existente is not None:

        conexao.close()

        return resposta_erro(
            "Já existe uma categoria com esse nome",
            409
        )

    try:

        cursor = conexao.execute(
            """
            INSERT INTO categorias (nome)
            VALUES (?)
            """,
            (nome,)
        )

        conexao.commit()

    except sqlite3.IntegrityError:

        conexao.close()

        return resposta_erro(
            "Já existe uma categoria com esse nome",
            409
        )

    nova_id = cursor.lastrowid

    conexao.close()

    return jsonify({
        "id": nova_id,
        "nome": nome
    }), 201


@app.route("/api/categorias/<int:categoria_id>", methods=["DELETE"])
def excluir_categoria(categoria_id):

    conexao = obter_conexao()

    categoria_existente = conexao.execute(
        """
        SELECT id
        FROM categorias
        WHERE id = ?
        """,
        (categoria_id,)
    ).fetchone()

    if categoria_existente is None:

        conexao.close()

        return resposta_erro(
            "Categoria não encontrada",
            404
        )

    conexao.execute(
        """
        UPDATE produtos
        SET categoria_id = NULL
        WHERE categoria_id = ?
        """,
        (categoria_id,)
    )

    conexao.execute(
        """
        DELETE FROM categorias
        WHERE id = ?
        """,
        (categoria_id,)
    )

    conexao.commit()
    conexao.close()

    return jsonify({
        "mensagem": "Categoria excluída com sucesso"
    })


# ============================================================================
# API DE USUÁRIOS
# ============================================================================

@app.route("/api/usuarios", methods=["GET"])
def listar_usuarios():

    conexao = obter_conexao()

    linhas = conexao.execute("""
        SELECT
            id,
            nome,
            email,
            telefone,
            cpf,
            data_nascimento,
            categoria,
            data_cadastro
        FROM usuarios
        ORDER BY id
    """).fetchall()

    conexao.close()

    usuarios = [
        usuario_para_dict(linha)
        for linha in linhas
    ]

    return jsonify(usuarios)


@app.route("/api/usuarios", methods=["POST"])
def criar_usuario():

    dados = request.get_json(
        silent=True
    ) or {}

    nome = dados.get("nome")
    email = dados.get("email")
    telefone = dados.get("telefone")
    cpf = dados.get("cpf")
    data_nascimento = dados.get("data_nascimento")
    categoria = dados.get("categoria")
    senha = dados.get("senha")


    campos_obrigatorios = {
        "nome": nome,
        "email": email,
        "telefone": telefone,
        "cpf": cpf,
        "data_nascimento": data_nascimento,
        "categoria": categoria,
        "senha": senha,
    }

    for campo, valor in campos_obrigatorios.items():

        if not valor:

            return resposta_erro(
                f"O campo '{campo}' é obrigatório"
            )


    if len(senha) < 6:

        return resposta_erro(
            "A senha deve ter no mínimo 6 caracteres"
        )


    conexao = obter_conexao()


    email_existente = conexao.execute(
        """
        SELECT id
        FROM usuarios
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    if email_existente is not None:

        conexao.close()

        return resposta_erro(
            "Já existe um usuário com esse e-mail",
            409
        )


    cpf_existente = conexao.execute(
        """
        SELECT id
        FROM usuarios
        WHERE cpf = ?
        """,
        (cpf,)
    ).fetchone()

    if cpf_existente is not None:

        conexao.close()

        return resposta_erro(
            "Já existe um usuário com esse CPF",
            409
        )


    senha_hash = generate_password_hash(
        senha
    )


    try:

        cursor = conexao.execute("""
            INSERT INTO usuarios
            (
                nome,
                email,
                telefone,
                cpf,
                data_nascimento,
                categoria,
                senha_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            nome,
            email,
            telefone,
            cpf,
            data_nascimento,
            categoria,
            senha_hash
        ))

        conexao.commit()

    except sqlite3.IntegrityError:

        conexao.close()

        return resposta_erro(
            "E-mail ou CPF já cadastrado",
            409
        )


    novo_id = cursor.lastrowid


    linha = conexao.execute("""
        SELECT
            id,
            nome,
            email,
            telefone,
            cpf,
            data_nascimento,
            categoria,
            data_cadastro
        FROM usuarios
        WHERE id = ?
    """, (novo_id,)).fetchone()

    conexao.close()

    return jsonify(
        usuario_para_dict(linha)
    ), 201


# ============================================================================
# LOGIN
# ============================================================================

@app.route("/api/login", methods=["POST"])
def login():

    dados = request.get_json(
        silent=True
    ) or {}

    email = dados.get("email")
    senha = dados.get("senha")

    if not email or not senha:

        return resposta_erro(
            "Informe email e senha"
        )


    conexao = obter_conexao()

    usuario = conexao.execute(
        """
        SELECT *
        FROM usuarios
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    conexao.close()


    if usuario is None:

        return resposta_erro(
            "E-mail ou senha inválidos",
            401
        )


    if not check_password_hash(
        usuario["senha_hash"],
        senha
    ):

        return resposta_erro(
            "E-mail ou senha inválidos",
            401
        )


    return jsonify({
        "mensagem": "Login realizado com sucesso",
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"]
        }
    })


# ============================================================================
# API DO CARRINHO
# ============================================================================

@app.route("/api/carrinho/<int:usuario_id>", methods=["GET"])
def obter_carrinho(usuario_id):

    conexao = obter_conexao()

    itens_linhas = conexao.execute("""
        SELECT
            ci.id,
            ci.produto_id,
            ci.quantidade,
            p.nome,
            p.imagem,
            p.preco
        FROM carrinho_itens ci
        JOIN produtos p
            ON ci.produto_id = p.id
        WHERE ci.usuario_id = ?
        ORDER BY ci.id
    """, (usuario_id,)).fetchall()

    conexao.close()


    itens = []
    total = 0.0


    for linha in itens_linhas:

        subtotal = round(
            linha["preco"] * linha["quantidade"],
            2
        )

        total += subtotal


        itens.append({
            "id": linha["id"],
            "produto_id": linha["produto_id"],
            "nome": linha["nome"],
            "imagem": linha["imagem"],
            "preco": linha["preco"],
            "quantidade": linha["quantidade"],
            "subtotal": subtotal
        })


    return jsonify({
        "itens": itens,
        "total": round(total, 2)
    })


@app.route("/api/carrinho/<int:usuario_id>", methods=["POST"])
def adicionar_ao_carrinho(usuario_id):

    dados = request.get_json(
        silent=True
    ) or {}

    produto_id = dados.get("produto_id")
    quantidade = dados.get(
        "quantidade",
        1
    )


    if produto_id is None:

        return resposta_erro(
            "O campo 'produto_id' é obrigatório"
        )


    try:

        quantidade = int(quantidade)

    except (ValueError, TypeError):

        return resposta_erro(
            "O campo 'quantidade' deve ser um número inteiro"
        )


    if quantidade <= 0:

        return resposta_erro(
            "A quantidade deve ser maior que 0"
        )


    conexao = obter_conexao()


    usuario = conexao.execute(
        """
        SELECT id
        FROM usuarios
        WHERE id = ?
        """,
        (usuario_id,)
    ).fetchone()

    if usuario is None:

        conexao.close()

        return resposta_erro(
            "Usuário não encontrado",
            404
        )


    produto = conexao.execute(
        """
        SELECT id
        FROM produtos
        WHERE id = ?
        """,
        (produto_id,)
    ).fetchone()

    if produto is None:

        conexao.close()

        return resposta_erro(
            "Produto não encontrado",
            404
        )


    item_existente = conexao.execute("""
        SELECT
            id,
            quantidade
        FROM carrinho_itens
        WHERE usuario_id = ?
        AND produto_id = ?
    """, (
        usuario_id,
        produto_id
    )).fetchone()


    if item_existente is not None:

        nova_quantidade = (
            item_existente["quantidade"]
            + quantidade
        )

        conexao.execute(
            """
            UPDATE carrinho_itens
            SET quantidade = ?
            WHERE id = ?
            """,
            (
                nova_quantidade,
                item_existente["id"]
            )
        )

    else:

        conexao.execute("""
            INSERT INTO carrinho_itens
            (
                usuario_id,
                produto_id,
                quantidade
            )
            VALUES (?, ?, ?)
        """, (
            usuario_id,
            produto_id,
            quantidade
        ))


    conexao.commit()
    conexao.close()


    return jsonify({
        "mensagem": "Produto adicionado ao carrinho"
    }), 201


@app.route(
    "/api/carrinho/<int:usuario_id>/<int:item_id>",
    methods=["PUT"]
)
def atualizar_item_carrinho(
    usuario_id,
    item_id
):

    dados = request.get_json(
        silent=True
    ) or {}

    quantidade = dados.get(
        "quantidade"
    )


    if quantidade is None:

        return resposta_erro(
            "O campo 'quantidade' é obrigatório"
        )


    try:

        quantidade = int(
            quantidade
        )

    except (ValueError, TypeError):

        return resposta_erro(
            "O campo 'quantidade' deve ser um número inteiro"
        )


    conexao = obter_conexao()


    item = conexao.execute("""
        SELECT id
        FROM carrinho_itens
        WHERE id = ?
        AND usuario_id = ?
    """, (
        item_id,
        usuario_id
    )).fetchone()


    if item is None:

        conexao.close()

        return resposta_erro(
            "Item do carrinho não encontrado",
            404
        )


    if quantidade <= 0:

        conexao.execute(
            """
            DELETE FROM carrinho_itens
            WHERE id = ?
            """,
            (item_id,)
        )

        mensagem = (
            "Item removido do carrinho"
        )

    else:

        conexao.execute(
            """
            UPDATE carrinho_itens
            SET quantidade = ?
            WHERE id = ?
            """,
            (
                quantidade,
                item_id
            )
        )

        mensagem = (
            "Quantidade atualizada"
        )


    conexao.commit()
    conexao.close()


    return jsonify({
        "mensagem": mensagem
    })


@app.route(
    "/api/carrinho/<int:usuario_id>/<int:item_id>",
    methods=["DELETE"]
)
def remover_item_carrinho(
    usuario_id,
    item_id
):

    conexao = obter_conexao()


    item = conexao.execute("""
        SELECT id
        FROM carrinho_itens
        WHERE id = ?
        AND usuario_id = ?
    """, (
        item_id,
        usuario_id
    )).fetchone()


    if item is None:

        conexao.close()

        return resposta_erro(
            "Item do carrinho não encontrado",
            404
        )


    conexao.execute(
        """
        DELETE FROM carrinho_itens
        WHERE id = ?
        """,
        (item_id,)
    )

    conexao.commit()
    conexao.close()


    return jsonify({
        "mensagem": "Item removido do carrinho"
    })


@app.route(
    "/api/carrinho/<int:usuario_id>",
    methods=["DELETE"]
)
def limpar_carrinho(usuario_id):

    conexao = obter_conexao()

    conexao.execute(
        """
        DELETE FROM carrinho_itens
        WHERE usuario_id = ?
        """,
        (usuario_id,)
    )

    conexao.commit()
    conexao.close()


    return jsonify({
        "mensagem": "Carrinho esvaziado com sucesso"
    })


# ============================================================================
# DASHBOARD ADMIN
# ============================================================================

@app.route("/api/dashboard", methods=["GET"])
def dashboard():

    conexao = obter_conexao()


    total_produtos = conexao.execute(
        """
        SELECT COUNT(*) AS total
        FROM produtos
        """
    ).fetchone()["total"]


    total_usuarios = conexao.execute(
        """
        SELECT COUNT(*) AS total
        FROM usuarios
        """
    ).fetchone()["total"]


    estatisticas_preco = conexao.execute("""
        SELECT
            COALESCE(SUM(preco), 0) AS valor_total,
            MIN(preco) AS preco_minimo,
            MAX(preco) AS preco_maximo,
            AVG(preco) AS preco_medio
        FROM produtos
    """).fetchone()


    produtos_por_categoria = conexao.execute("""
        SELECT
            c.nome AS categoria,
            COUNT(p.id) AS quantidade
        FROM categorias c
        LEFT JOIN produtos p
            ON p.categoria_id = c.id
        GROUP BY c.id, c.nome
        ORDER BY c.nome
    """).fetchall()


    conexao.close()


    def arredondar(valor):

        return (
            round(valor, 2)
            if valor is not None
            else 0
        )


    return jsonify({

        "total_produtos":
            total_produtos,

        "total_usuarios":
            total_usuarios,

        "valor_total":
            arredondar(
                estatisticas_preco[
                    "valor_total"
                ]
            ),

        "preco_minimo":
            arredondar(
                estatisticas_preco[
                    "preco_minimo"
                ]
            ),

        "preco_maximo":
            arredondar(
                estatisticas_preco[
                    "preco_maximo"
                ]
            ),

        "preco_medio":
            arredondar(
                estatisticas_preco[
                    "preco_medio"
                ]
            ),

        "produtos_por_categoria": [

            {
                "categoria":
                    linha["categoria"],

                "quantidade":
                    linha["quantidade"]
            }

            for linha
            in produtos_por_categoria
        ]
    })


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
