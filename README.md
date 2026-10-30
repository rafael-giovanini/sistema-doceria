# 🍰 Sistema de Doceria - Gestao Completa

Sistema web completo para gerenciamento de docerias: precificacao automatica de produtos, controle de estoque de materia-prima, registro de vendas, relatorios financeiros, graficos e exportacao em PDF/Excel.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Banco%20de%20Dados-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Suporte-2496ED?logo=docker&logoColor=white)
![Mobile](https://img.shields.io/badge/Mobile-Responsivo-25D366)
![License](https://img.shields.io/badge/Licenca-MIT-green)

## ✨ Funcionalidades

| Modulo | Descricao |
|---|---|
| 📦 **Estoque** | Cadastro de ingredientes, custo unitario automatico, alerta de estoque baixo |
| 📖 **Receitas** | Montagem de receitas, calculo de custo total e preco de venda por margem de lucro |
| 🛒 **Vendas** | Registro de vendas com baixa automatica no estoque |
| 💰 **Financeiro** | Total de vendas, custos, lucro liquido e quantidade de vendas |
| 📊 **Graficos** | Vendas por dia (linha) e por produto (barras), filtro de 7/30/90 dias |
| 📄 **Exportacao** | Relatorios em Excel (.xlsx) e PDF de vendas, estoque e receitas |
| 📱 **Mobile** | Interface totalmente responsiva para uso no celular |

## 🚀 Como rodar

### Opcao 1 - Docker (recomendado)
```bash
docker-compose up -d
```
Acesse: **http://localhost:8000**

### Opcao 2 - Manual
```bash
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Acesse: **http://localhost:8000**

### 📱 Usar no celular
Conecte o celular na mesma Wi-Fi e inicie com `--host 0.0.0.0`. Acesse `http://IP_DO_COMPUTADOR:8000`.

## 🧮 Logica de Precificacao
```
Preco de Venda = Custo Unitario / (1 - Margem de Lucro)
```
Exemplo: Custo R$ 5,00 | Margem 40% → 5 / 0,6 = **R$ 8,33**

## 📁 Estrutura do Projeto
```
doceria/
├── main.py              # Servidor FastAPI + endpoints da API
├── models.py            # Modelos do banco de dados (SQLAlchemy)
├── schemas.py           # Validacao de dados (Pydantic)
├── database.py          # Conexao com SQLite
├── requirements.txt     # Dependencias Python
├── Dockerfile           # Imagem Docker
├── docker-compose.yml   # Orquestracao Docker
├── .dockerignore        # Arquivos ignorados no build
├── .gitignore
├── README.md
└── static/
    └── index.html       # Interface web (mobile + graficos + exportacao)
```

## 💾 Backup
O banco de dados fica no arquivo `doceria.db`. Basta copia-lo para fazer backup de todos os dados. No Docker, o volume `doceria_data` persiste os dados automaticamente.

## 🔧 API Endpoints
- `GET/POST /api/ingredientes` — gerenciar ingredientes e estoque
- `PATCH /api/ingredientes/{id}/estoque` — ajustar estoque
- `GET/POST /api/receitas` — gerenciar receitas e precos
- `GET/POST /api/vendas` — registrar e listar vendas
- `GET /api/resumo-financeiro` — resumo financeiro
- `GET /api/graficos/vendas-por-dia` — dados do grafico de vendas por dia
- `GET /api/graficos/vendas-por-produto` — dados do grafico por produto
- `GET /api/exportar/vendas-excel|estoque-excel|receitas-excel` — download Excel
- `GET /api/exportar/vendas-pdf` — download PDF

## 📄 Licenca
MIT - uso livre.
