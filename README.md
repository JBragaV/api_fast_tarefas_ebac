# API FastAPI - Livros/Tarefas EBAC

![Build](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)

> Uma API com FastAPI de estudos do curso de Backend EBAC.

## 📋 Sobre o Projeto

Projeto de estudo desenvolvido durante o curso de Backend da EBAC, com o
objetivo de praticar a construção de uma API REST utilizando FastAPI,
SQLAlchemy e SQLite, seguindo uma organização de pastas
inspirada em boas práticas de arquitetura.

## ✨ Funcionalidades

- [ ] CRUD de tarefas
- [ ] Persistência com SQLAlchemy + SQLite
- [ ] Configuração centralizada do sistema

## 🛠️ Tecnologias Utilizadas

- Python 3.13+
- FastAPI (`fastapi[standard]`)
- SQLAlchemy 2.x
- aiosqlite
- Uvicorn
- Poetry (gerenciamento de dependências)

## 📁 Estrutura do Projeto

```
PROJETO/
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth_usuarios.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── configs.py        # Configurações do sistema (ex.: URL do banco)
│   ├── database/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── lembretes.py
│   │   │   ├── tarefa.py
│   │   │   └── usuario.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── base_schema.py
│   │   │   ├── respostas_schema.py
│   │   │   ├── tarefa_schema.py
│   │   │   └── usuario_schema.py
│   │   ├── __init__.py
│   │   └── session.py
│   ├── router
│   │   ├── __init__.py
│   │   ├── tarefas.py
│   │   └── usuarios.py
│   ├── tests
│   │   ├── __init__.py
│   ├── utils
│   │   ├── __init__.py
│   │   └── utils.py
│   └── main.py
├── poetry.lock
├── pyproject.toml
└── README.md
```

## ⚙️ Pré-requisitos

- Python 3.13 ou superior
- Poetry instalado

## 🚀 Instalação

```bash
# Clone o repositório
git clone <link-do-repositorio>

# Acesse a pasta do projeto
cd pasta_projeto

# Instale as dependências com Poetry
poetry install
```

## ⚙️ Configuração

O nome/caminho do banco de dados pode ser alterado em `app/core/configs.py`,
na variável `DATABASE_URL` da classe `SysConfig`:

```python
DATABASE_URL = "sqlite:///livraria_ebac.db"
```

> No futuro será adotado `python-dotenv` para mover essa configuração para
> um arquivo `.env` (ainda não implementado).

## ▶️ Como Usar

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://127.0.0.1:8000`, com a documentação
interativa em `http://127.0.0.1:8000/docs`.

## 🗺️ Roadmap

- [ ] Rotas assincronas
- [ ] Adicionar autenticação
- [ ] Escrever testes automatizados

## 📄 Licença

Projeto de estudo, sem licença definida.

## 👤 Autor

**JBragaV**

- E-mail: jocimarcaiadobraga@gmail.com