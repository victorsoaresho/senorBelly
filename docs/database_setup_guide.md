# Guia de Configuração de Banco de Dados: PostgreSQL + SQLAlchemy + Alembic

Este guia fornece um passo a passo detalhado, focado em boas práticas de Python e orientado a TDD (Test-Driven Development), para configurar e integrar um banco de dados PostgreSQL ao seu projeto utilizando SQLAlchemy e Alembic.

## 1. Configuração do Docker Compose

Para garantir um ambiente de desenvolvimento isolado e reproduzível, utilizaremos o Docker para hospedar nosso banco de dados PostgreSQL.

Crie um arquivo `docker-compose.yml` na raiz do seu projeto com o seguinte conteúdo:

```yaml
services:
  db:
    image: postgres:16-alpine
    container_name: senorbelly_db
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secretpassword
      POSTGRES_DB: senorbelly
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d senorbelly"]
      interval: 5s
      timeout: 5s
      retries: 5

  db_test:
    image: postgres:16-alpine
    container_name: senorbelly_db_test
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secretpassword
      POSTGRES_DB: senorbelly_test
    ports:
      - "5433:5432"
    tmpfs:
      - /var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d senorbelly_test"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

> [!TIP]
> Utilizamos o banco `db_test` usando `tmpfs` em vez de volumes em disco para o banco de testes. Isso garante que os testes rodem em memória de forma muito mais rápida, e os dados são descartados após o uso.

Suba os bancos de dados executando:
```bash
docker compose up -d
```

## 2. Instalação de Dependências

Como o projeto está utilizando o `uv` como gerenciador de pacotes, instale as dependências necessárias para a integração do banco de dados:

```bash
uv add sqlalchemy alembic psycopg2-binary
```
*(Nota: `psycopg2-binary` ou `psycopg` (v3) é o driver necessário para que o SQLAlchemy se comunique com o PostgreSQL).*

Para os testes, você já possui o `pytest`, mas talvez seja interessante adicionar variáveis de ambiente nos testes:
```bash
uv add --dev pytest-env
```

## 3. Integração Orientada a TDD (Test-Driven Development)

No TDD, o ciclo é: **Red** (escreva um teste que falha), **Green** (escreva o código para o teste passar), **Refactor** (melhore o código).

### Fase RED: Criando o Teste de Conexão

Crie um arquivo `tests/test_database.py` para testar se nossa aplicação consegue se conectar ao banco.

```python
import pytest
from sqlalchemy import text
from app.database import get_db_session

def test_database_connection():
    # Arrange & Act
    session = get_db_session()
    result = session.execute(text("SELECT 1")).scalar()
    
    # Assert
    assert result == 1
```

Ao rodar `pytest tests/test_database.py`, o teste **falhará** (RED), pois o módulo `app.database` não existe.

### Fase GREEN: Implementando a Conexão

Agora, vamos criar a configuração real para o SQLAlchemy.
Crie o arquivo `app/database.py`:

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Lê a URL do banco a partir da variável de ambiente, ou usa um valor padrão (útil para dev)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:secretpassword@localhost:5432/senorbelly"
)

# Configuração da engine do SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Criador de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para os modelos declarativos
Base = declarative_base()

def get_db_session():
    """Retorna uma nova sessão de banco de dados."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
```

Rode o teste novamente. Se o seu contêiner do Docker estiver rodando, o teste deve **passar** (GREEN).

## 4. Configurando o Alembic para Migrações

O Alembic é a ferramenta padrão de migrações (controle de versão do banco de dados) para o SQLAlchemy.

### Passo 4.1: Inicializando o Alembic

Na raiz do projeto, execute o comando:

```bash
alembic init migrations
```
Isso criará a pasta `migrations/` e o arquivo `alembic.ini`.

### Passo 4.2: Configurando o Alembic

Abra o arquivo `alembic.ini` e atualize a linha `sqlalchemy.url`:

```ini
# alembic.ini (remova a linha sqlalchemy.url atual e adicione a sua ou deixe em branco para passar dinamicamente via env.py)
sqlalchemy.url = postgresql://admin:secretpassword@localhost:5432/senorbelly
```

A seguir, configure o `env.py` do Alembic (`migrations/env.py`) para que ele consiga ler os metadados dos seus modelos. Atualize a seção onde o `target_metadata` é definido:

```python
# migrations/env.py
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Adiciona o diretório raiz ao sys.path para o Alembic achar o pacote "app"
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base
# Importe seus modelos aqui para que o Alembic os reconheça, ex:
# from app.models.user import User

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Configura o target_metadata com o Base do SQLAlchemy
target_metadata = Base.metadata

# Restante do arquivo env.py padrão...
```

### Passo 4.3: Criando e Aplicando a Primeira Migração

Para seguir o TDD, vamos criar um modelo de teste em `app/models/user.py`:

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
```

Certifique-se de importar este modelo no `migrations/env.py` conforme mencionado acima.

Gere a migração automaticamente:

```bash
alembic revision --autogenerate -m "Create users table"
```

Aplique a migração no banco de dados:

```bash
alembic upgrade head
```

## 5. Práticas Avançadas de Testes (TDD com Banco de Dados)

Ao testar aplicações com banco de dados, é crucial usar o **banco de testes** (`db_test` no nosso Docker Compose que roda na porta 5433) e garantir que o banco esteja limpo antes de cada teste.

Crie um arquivo `conftest.py` na pasta `tests/` para configurar os fixtures do Pytest:

```python
# tests/conftest.py
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

# Força a URL para o banco de testes
TEST_DATABASE_URL = "postgresql://admin:secretpassword@localhost:5433/senorbelly_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_db():
    # Cria as tabelas no banco de testes antes de rodar a suíte
    Base.metadata.create_all(bind=engine)
    yield
    # Remove as tabelas no final da sessão
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def session(test_db):
    """Fornece uma sessão transacional para cada teste e faz rollback no final."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

> [!IMPORTANT]
> O padrão utilizado no fixture `session` abre uma transação por teste e executa o `rollback` ao final de cada função de teste. Isso garante que os testes fiquem perfeitamente isolados (um não afeta o outro) e extremamente rápidos, pois nada é efetivamente "comitado" no banco de testes físico.

Agora você pode escrever testes de CRUD seguindo o fluxo Red-Green-Refactor:

```python
# tests/test_user.py
from app.models.user import User

def test_create_user_success(session):
    # Arrange
    new_user = User(username="joao", email="joao@example.com")
    
    # Act
    session.add(new_user)
    session.commit() # O commit ocorre apenas na transação aninhada do fixture
    
    # Assert
    saved_user = session.query(User).filter_by(email="joao@example.com").first()
    assert saved_user is not None
    assert saved_user.username == "joao"
```

## Referências Oficiais
Para aprofundar seu conhecimento e resolver dúvidas complexas, consulte as documentações oficiais:

- [Docker Hub - Imagem do PostgreSQL](https://hub.docker.com/_/postgres)
- [Documentação Oficial do SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Documentação Oficial do Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [Documentação Oficial do Pytest](https://docs.pytest.org/en/stable/)
