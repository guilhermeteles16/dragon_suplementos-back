# -*- coding: utf-8 -*-
"""
test_api.py

Testes automáticos BÁSICOS para a API do Dragon Suplementos.

IMPORTANTE: o servidor (app.py) precisa estar rodando em
http://localhost:5000 ANTES de executar este arquivo.

Como executar:

    1. Em um terminal, inicie o servidor:
        python app.py

    2. Em outro terminal, execute os testes:
        python test_api.py

Este arquivo testa, na ordem:
    - Rota inicial
    - Listagem de categorias
    - Criação e listagem de produtos
    - Criação de usuário
    - Login
    - Dashboard

Usa apenas a biblioteca 'requests' e dados únicos (com timestamp) para
não conflitar com testes anteriores.
"""

import time
import requests

API_URL = "http://localhost:5000"


def testar_rota_inicial():
    resposta = requests.get(f"{API_URL}/")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["status"] == "online"
    print("[OK] Rota inicial funcionando.")


def testar_listar_categorias():
    resposta = requests.get(f"{API_URL}/api/categorias")
    assert resposta.status_code == 200
    categorias = resposta.json()
    assert isinstance(categorias, list)
    assert len(categorias) > 0
    print(f"[OK] {len(categorias)} categoria(s) encontrada(s).")
    return categorias


def testar_criar_e_listar_produto(categoria_id):
    nome_produto = f"Produto Teste {int(time.time())}"

    resposta = requests.post(f"{API_URL}/api/produtos", json={
        "nome": nome_produto,
        "imagem": "imgs/teste.png",
        "descricao": "Produto criado pelo teste automático",
        "preco": 99.90,
        "categoria_id": categoria_id
    })
    assert resposta.status_code == 201
    produto_criado = resposta.json()
    assert produto_criado["nome"] == nome_produto
    print(f"[OK] Produto criado com id {produto_criado['id']}.")

    resposta = requests.get(f"{API_URL}/api/produtos")
    assert resposta.status_code == 200
    produtos = resposta.json()
    assert any(p["id"] == produto_criado["id"] for p in produtos)
    print(f"[OK] Produto encontrado na listagem ({len(produtos)} produtos no total).")

    return produto_criado


def testar_criar_usuario_e_login():
    email_unico = f"teste{int(time.time())}@email.com"
    cpf_unico = str(int(time.time()))[-11:].zfill(11)
    senha = "123456"

    resposta = requests.post(f"{API_URL}/api/usuarios", json={
        "nome": "Usuário de Teste",
        "email": email_unico,
        "telefone": "11999999999",
        "cpf": cpf_unico,
        "data_nascimento": "2000-01-01",
        "categoria": "Cliente",
        "senha": senha
    })
    assert resposta.status_code == 201
    usuario_criado = resposta.json()
    assert "senha_hash" not in usuario_criado
    print(f"[OK] Usuário criado com id {usuario_criado['id']}.")

    # Login com senha correta
    resposta = requests.post(f"{API_URL}/api/login", json={
        "email": email_unico,
        "senha": senha
    })
    assert resposta.status_code == 200
    print("[OK] Login com senha correta funcionou.")

    # Login com senha errada
    resposta = requests.post(f"{API_URL}/api/login", json={
        "email": email_unico,
        "senha": "senha_errada"
    })
    assert resposta.status_code == 401
    print("[OK] Login com senha errada foi bloqueado corretamente.")

    return usuario_criado


def testar_dashboard():
    resposta = requests.get(f"{API_URL}/api/dashboard")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert "total_produtos" in dados
    assert "total_usuarios" in dados
    assert "produtos_por_categoria" in dados
    print("[OK] Dashboard retornou os dados calculados corretamente.")


def executar_todos_os_testes():
    print("Iniciando testes da API Dragon Suplementos...\n")

    testar_rota_inicial()
    categorias = testar_listar_categorias()
    testar_criar_e_listar_produto(categorias[0]["id"])
    testar_criar_usuario_e_login()
    testar_dashboard()

    print("\nTodos os testes foram concluídos com sucesso!")


if __name__ == "__main__":
    try:
        executar_todos_os_testes()
    except requests.exceptions.ConnectionError:
        print("ERRO: não foi possível conectar à API.")
        print("Verifique se o servidor está rodando com: python app.py")
    except AssertionError as erro:
        print(f"FALHA em um dos testes: {erro}")
