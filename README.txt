# 🍰 Sistema de Doceria - Completo

Sistema completo com banco de dados, precificacao, estoque, vendas, financeiro, graficos e exportacao.

## 📦 O que tem dentro

- **Estoque de materia-prima** - cadastro de ingredientes com custo unitario automatico
- **Receitas e Precificacao** - monte a receita, defina a margem de lucro, o preco e calculado sozinho
- **Vendas** - registre vendas e o estoque diminui automaticamente
- **Financeiro** - total de vendas, custos, lucro liquido
- **Graficos** - vendas por dia e por produto (7, 30 ou 90 dias)
- **Exportacao** - Excel (.xlsx) e PDF de vendas, estoque e receitas
- **Mobile** - interface responsiva para celular

## 🚀 Como instalar (3 passos)

### 1. Instale o Python
Baixe em https://www.python.org/downloads/ e marque "Add Python to PATH" durante a instalacao.

### 2. Instale as bibliotecas
Abra o terminal (Prompt de Comando / PowerShell), entre na pasta `doceria` e rode:
```
pip install -r requirements.txt
```

### 3. Inicie o sistema
```
python -m uvicorn main:app --reload
```

Abra no navegador: **http://127.0.0.1:8000**

## 📱 Usar no celular
Conecte o celular na mesma Wi-Fi do computador. Descubra o IP do computador (comando `ipconfig` no Windows ou `ifconfig` no Linux/Mac) e acesse no celular: `http://SEU_IP:8000`. Para liberar acesso na rede, inicie com:
```
python -m uvicorn main:app --host 0.0.0.0 --reload
```

## 💾 Backup
O banco de dados e o arquivo `doceria.db` (criado automaticamente na primeira vez). Copie esse arquivo para fazer backup de tudo.

## 📁 Estrutura
```
doceria/
├── main.py            # Servidor + API (todas as funcoes)
├── models.py          # Tabelas do banco de dados
├── schemas.py         # Validacao de dados
├── database.py        # Conexao com SQLite
├── requirements.txt   # Bibliotecas necessarias
├── README.txt         # Este arquivo
└── static/
    └── index.html     # Interface (mobile + graficos + exportacao)
```

## ❓ Duvidas
- Para parar o sistema: `Ctrl+C` no terminal
- Para reiniciar: rode o passo 3 novamente
- Os dados ficam salvos mesmo apos fechar o navegador
