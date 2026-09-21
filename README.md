# Dragon Suplementos — Backend

Backend do projeto **Dragon Suplementos**, desenvolvido como projeto do curso de Desenvolvimento de Sistemas.

O backend é responsável pelo processamento das informações da loja, comunicação com o banco de dados, gerenciamento de usuários, produtos, categorias, carrinho e fornecimento de dados para o frontend através de uma API REST.

## Autores

**Guilherme Teles da Silva**
**Arthur Uezu da Cruz**

### Com auxílio de

**Gustavo Moraes**
**Mateus Valente**

**Etec de Poá — 2026**
**2º DSN**

---

## Tecnologias utilizadas

* Python
* Flask
* SQLite
* Flask-CORS
* Werkzeug
* API REST
* Render para hospedagem

## Estrutura do projeto

```text
dragon-suplementos-back-end/
│
├── app.py
├── banco_dados.py
├── loja_suplementos.db
├── requirements.txt
│
├── uploads/
│   └── imagens dos produtos
│
└── outros arquivos de configuração
```

## Responsabilidades do Backend

O backend é responsável por:

* Gerenciar usuários;
* Realizar cadastro de clientes;
* Realizar login;
* Gerenciar produtos;
* Gerenciar categorias;
* Controlar estoque;
* Gerenciar itens do carrinho;
* Fornecer informações para o dashboard;
* Receber e armazenar imagens dos produtos;
* Realizar a comunicação entre o frontend e o banco de dados.

---

## Banco de Dados

O sistema utiliza **SQLite** para armazenamento dos dados.

### Tabela `usuarios`

Armazena as informações dos clientes cadastrados.

Principais campos:

```text
id
nome
email
telefone
cpf
data_nascimento
categoria
senha_hash
data_cadastro
```

O e-mail e o CPF são únicos para evitar cadastros duplicados.

### Tabela `produtos`

Armazena os produtos disponíveis na loja.

Principais campos:

```text
id
nome
imagem
descricao
preco
estoque
categoria_id
data_cadastro
```

### Tabela `categorias`

Armazena as categorias dos produtos.

Categorias utilizadas:

```text
suplementos
roupas
acessorios
equipamentos
```

### Tabela `carrinho_itens`

Relaciona os usuários aos produtos adicionados ao carrinho.

Principais campos:

```text
id
usuario_id
produto_id
quantidade
```

---

## API

O frontend se comunica com o backend através de requisições HTTP.

URL do backend:

```text
https://dragon-suplementos-back-end.onrender.com/
```

### Produtos

```text
GET    /api/produtos
GET    /api/produtos/<id>
POST   /api/produtos
PUT    /api/produtos/<id>
DELETE /api/produtos/<id>
```

Essas rotas permitem consultar, cadastrar, editar e excluir produtos.

### Categorias

```text
GET /api/categorias
```

Retorna as categorias disponíveis para utilização no sistema.

### Usuários

```text
POST /api/usuarios
POST /api/login
```

A primeira rota realiza o cadastro de novos usuários e a segunda realiza a autenticação.

As senhas não são armazenadas diretamente. O sistema utiliza uma versão protegida da senha através de hash.

### Carrinho

```text
POST /api/carrinho/<usuario_id>
```

Permite adicionar produtos ao carrinho de um usuário.

O `usuario_id` identifica qual cliente está realizando a operação.

### Dashboard

```text
GET /api/dashboard
```

Fornece informações utilizadas pelo dashboard administrativo, como:

* Valor total dos produtos;
* Maior preço;
* Menor preço;
* Preço médio;
* Indicadores da loja.

---

## Cadastro de Produtos

O administrador envia os dados do produto através de uma requisição `POST`.

São recebidos:

```text
nome
categoria
preco
estoque
descricao
imagem
```

O backend valida os dados, identifica a categoria correspondente e salva o produto no banco de dados.

As imagens enviadas são armazenadas na pasta `uploads`.

---

## Controle de Estoque

Cada produto possui uma quantidade de estoque.

O sistema verifica se o valor informado é válido e não permite estoque negativo.

Produtos com estoque igual a zero são considerados indisponíveis no dashboard.

---

## Integração com o Frontend

O frontend utiliza a `Fetch API` para realizar requisições ao backend.

Exemplo:

```javascript
const resposta = await fetch(
    "https://dragon-suplementos-back-end.onrender.com/api/produtos"
);
```

O backend processa a solicitação, consulta ou altera o banco de dados e retorna as informações em formato JSON.

---

## CORS

O backend utiliza **Flask-CORS** para permitir que o frontend hospedado separadamente possa realizar requisições à API.

Isso possibilita a comunicação entre:

```text
Frontend
Netlify
       ↓
      API
       ↓
Backend
Render
       ↓
SQLite
```

---

## Tratamento de dados

O backend realiza validações para evitar dados inválidos, incluindo:

* Campos obrigatórios;
* Preços negativos;
* Estoque negativo;
* Categorias inexistentes;
* E-mails duplicados;
* CPFs duplicados;
* Usuários inexistentes;
* Produtos inexistentes.

As respostas da API são enviadas em formato JSON para facilitar a integração com o frontend.

---

## Hospedagem

O backend está hospedado na plataforma **Render**.

URL:

```text
https://dragon-suplementos-back-end.onrender.com/
```

O frontend hospedado no Netlify utiliza essa API para acessar os dados do sistema.

---

## Como executar localmente

### 1. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 2. Criar/configurar o banco de dados

Execute:

```bash
python banco_dados.py
```

### 3. Executar o servidor

```bash
python app.py
```

O servidor ficará disponível localmente, normalmente em:

```text
http://127.0.0.1:5000
```

---

## Fluxo do Backend

```text
Frontend
   ↓
Requisição HTTP
   ↓
API Flask
   ↓
Validação dos dados
   ↓
Banco de dados SQLite
   ↓
Processamento
   ↓
Resposta JSON
   ↓
Frontend
```

---

## Projeto

**Dragon Suplementos**

Projeto DS — Programação Web | Curso de Desenvolvimento de Sistemas

**Etec de Poá — 2026**
**2º DSN**

**Criado por Guilherme Teles da Silva e Arthur Uezu da Cruz**
**Com auxílio de Gustavo Moraes e Mateus Valente**
