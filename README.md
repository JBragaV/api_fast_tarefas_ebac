# API FastAPI - Livros/Tarefas EBAC

![Build](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![Docker](https://img.shields.io/badge/docker-ready-2496ED)

> Uma API com FastAPI de estudos do curso de Backend EBAC.

## 📋 Sobre o Projeto

Projeto de estudo desenvolvido durante o curso de Backend da EBAC, com o
objetivo de praticar a construção de uma API REST utilizando FastAPI,
SQLAlchemy e SQLite, seguindo uma organização de pastas
inspirada em boas práticas de arquitetura, e containerizado com Docker
para garantir um ambiente de desenvolvimento consistente e replicável.

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
- Docker / Docker Compose

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

Escolha uma das opções abaixo:

**Opção A — Com Docker (recomendado, não exige Python/Poetry instalados)**
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (já incluso no Docker Desktop)

**Opção B — Execução local**
- Python 3.13 ou superior
- Poetry instalado

## 🚀 Instalação e Execução

### Opção A — Com Docker

```bash
# Clone o repositório
git clone https://github.com/JBragaV/api_fast_tarefas_ebac.git
git clone https://github.com/JBragaV/api_fast_tarefas_ebac.gitk
cd pasta_projeto

# Copie o arquivo de variáveis de ambiente de exemplo
cp .env.example .env

# Suba a aplicação (build da imagem + execução em segundo plano)
docker compose up --build -d
```

A API estará disponível em `http://localhost:8000`, com a documentação
interativa em `http://localhost:8000/docs`.

O código-fonte é montado como volume dentro do container, e o servidor
roda com `--reload` — qualquer alteração salva nos arquivos `.py` locais
reinicia a aplicação automaticamente, sem precisar rebuildar a imagem.

**Comandos úteis:**

```bash
docker compose logs -f       # acompanhar logs em tempo real
docker compose down          # parar e remover os containers
docker compose exec app bash # abrir um shell dentro do container
```

### Opção B — Execução local

```bash
# Clone o repositório
git clone https://github.com/JBragaV/api_fast_tarefas_ebac.git
cd pasta_projeto

# Instale as dependências com Poetry
poetry install

# Rode a aplicação
poetry run uvicorn main:app --reload
```

A API estará disponível em `http://127.0.0.1:8000`, com a documentação
interativa em `http://127.0.0.1:8000/docs`.

## ⚙️ Configuração

O nome/caminho do banco de dados pode ser alterado em `core/configs.py`,
na variável `DATABASE_URL` da classe `SysConfig`:

```python
DATABASE_URL = "sqlite:///livraria_ebac.db"
```

> Ao rodar via Docker Compose, variáveis definidas no arquivo `.env` são
> injetadas automaticamente no container através do `env_file` do
> `docker-compose.yml` — isso funciona independente do `python-dotenv`,
> que só é necessário se você quiser carregar o `.env` manualmente ao
> rodar a aplicação **fora** do Docker (Opção B acima).

## 🗺️ Roadmap

- [ ] Rotas assíncronas
- [ ] Adicionar autenticação
- [ ] Escrever testes automatizados

## 📄 Licença

Projeto de estudo, sem licença definida.

## 👤 Autor

**JBragaV**

- E-mail: jocimarcaiadobraga@gmail.com