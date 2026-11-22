# E-Service - Sistema de Gestão de Projetos Industriais

Sistema de gerenciamento e governança ponta a ponta do fluxo de engenharia de aplicação e projetos industriais, eliminando planilhas descentralizadas e garantindo rastreabilidade, controle de SLA e catálogo centralizado.

---

## 🛠️ Stack Tecnológica

* **Backend**: Python 3.10+, Django 5+, Django REST Framework (DRF), SimpleJWT.
* **Banco de Dados (Estratégia Híbrida)**:
  * **MySQL 8.0** para desenvolvimento local e produção.
  * **SQLite em memória** (`:memory:`) exclusivamente para testes automatizados.
* **Object Storage**: `django-storages` + `boto3` apontando para **MinIO** (desenvolvimento local) e **AWS S3** (produção).
* **Geradores de Documentos**: `html2docx` (Word `.docx`) e `WeasyPrint` (PDF).
* **Frontend**: Vue 3 (Composition API / `<script setup>`), Pinia, Tailwind CSS, TipTap Editor e API Fetch nativa (**Axios proibido**).

---

## 📂 Arquitetura de Diretórios

```
E-Service_WorkSpace/
├── documentation/               # Especificações, diagramas Mermaid e regras de negócio
├── docker-compose.yml           # MySQL 8.0 + MinIO + MinIO Client
├── backend/                     # Projeto Django
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/                  # Configurações modulares
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py   # MySQL local
│   │   │   ├── production.py    # MySQL prod + S3
│   │   │   └── test.py          # SQLite em memória
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/                    # Domínios de negócio
│   │   ├── core/                # BaseUUIDModel, TimeStampedModel
│   │   ├── authentication/      # Custom User e perfis (Vendedor, Gestor, Técnico, Comercial)
│   │   ├── clientes/            # Entidade Cliente e contatos industriais
│   │   ├── catalogo/            # Catálogo Central e as 8 Famílias Base
│   │   ├── projetos/            # Projeto, Histórico com pausa de SLA, Comentários (Planner)
│   │   ├── agenda/              # Agenda Técnica com Trava Sequencial da Fila
│   │   ├── propostas/           # Propostas versionadas e BOM Hierárquica em árvore
│   │   ├── artefatos/           # Relatório Descritivo (TipTap), Topologia e Object Storage
│   │   └── servicos/            # Ordem de Serviço (OS) e Relatórios de Campo
│   └── tests/                   # Suíte de testes automatizados
└── frontend/                    # Aplicação Vue 3 + Vite + Tailwind + Pinia + TipTap
```

---

## 🚀 Como Executar o Ambiente Local

### 1. Subir a Infraestrutura (MySQL + MinIO)
```bash
docker compose up -d
```
* **MySQL**: porta `3306` (`eservice_db` / `eservice_user` / `eservice_password`)
* **MinIO Console**: `http://localhost:9001` (usuário: `minioadmin` / senha: `minioadminpassword`)

### 2. Configurar o Backend Python
```bash
# Ativar o ambiente virtual
.venv\Scripts\activate   # Windows

# Executar as migrações no MySQL
python backend/manage.py migrate

# Popular as 8 famílias base do Catálogo Central
python backend/manage.py seed_catalogo

# Iniciar o servidor de desenvolvimento
python backend/manage.py runserver
```

### 3. Rodar os Testes Automatizados (SQLite em memória)
```bash
python backend/manage.py test tests --settings=config.settings.test
```

---

## 🔒 Regras de Negócio Críticas Implementadas

1. **Trava Sequencial da Fila**: O método `pode_iniciar()` na `AgendaTecnica` impede o início de qualquer projeto se houver item anterior com `ordem_execucao` menor pendente na agenda do técnico.
2. **Pausa de SLA**: Transição para `AGUARDANDO_INFORMACAO` marca `pausa_contagem_tempo = True` no `HistoricoStatus`, congelando o SLA.
3. **BOM Hierárquica**: Itens vinculados obrigatoriamente ao `CatalogoItem`, com suporte a sub-itens recursivos (`parent_id`) e recálculo automático de totais da `Proposta`.
4. **Armazenamento Seguro de Binários**: Nenhum binário é persistido localmente no Django; relatórios e topologias são enviados diretamente para o bucket do Object Storage (`MinIO` / `S3`).
