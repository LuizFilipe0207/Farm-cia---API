# 💊 Farmácia API

API REST para gerenciamento de medicamentos e controle de estoque, desenvolvida com **Python**, **Flask** e **SQLite**.

---

## 🚀 Tecnologias Utilizadas

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)

---

## 📋 Funcionalidades

- ✅ Cadastro, listagem, atualização e remoção de medicamentos
- ✅ Filtro por nome, categoria e exigência de receita
- ✅ Controle de estoque por medicamento (entrada e saída de unidades)
- ✅ Alertas automáticos de estoque baixo e medicamentos próximos ao vencimento
- ✅ Validações de dados e retorno de erros claros

---

## 🗂️ Estrutura do Projeto

```
farmacia-api/
├── app/
│   ├── __init__.py         # Criação e configuração da aplicação Flask
│   ├── database.py         # Instância do SQLAlchemy
│   ├── models/
│   │   └── __init__.py     # Modelos: Medicamento e Estoque
│   └── routes/
│       ├── medicamentos.py # Endpoints de medicamentos
│       └── estoque.py      # Endpoints de estoque
├── run.py                  # Ponto de entrada
├── requirements.txt
└── .gitignore
```

---

## ⚙️ Como Executar

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/farmacia-api.git
cd farmacia-api
```

**2. Crie e ative o ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Execute a aplicação**
```bash
python run.py
```

A API estará disponível em `http://localhost:5000`

---

## 📡 Endpoints

### Medicamentos — `/api/medicamentos`

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/medicamentos/` | Lista todos os medicamentos |
| GET | `/api/medicamentos/?nome=dipirona` | Filtra por nome |
| GET | `/api/medicamentos/?categoria=analgesico` | Filtra por categoria |
| GET | `/api/medicamentos/?requer_receita=true` | Filtra por receita |
| GET | `/api/medicamentos/{id}` | Busca medicamento por ID |
| POST | `/api/medicamentos/` | Cadastra novo medicamento |
| PUT | `/api/medicamentos/{id}` | Atualiza medicamento |
| DELETE | `/api/medicamentos/{id}` | Remove medicamento |

### Estoque — `/api/estoque`

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/estoque/` | Lista estoque completo |
| GET | `/api/estoque/alertas` | Itens com estoque baixo ou próximos ao vencimento |
| GET | `/api/estoque/{medicamento_id}` | Estoque de um medicamento |
| POST | `/api/estoque/` | Registra estoque inicial |
| PUT | `/api/estoque/{medicamento_id}` | Atualiza dados do estoque |
| PATCH | `/api/estoque/{medicamento_id}/movimentar` | Registra entrada ou saída |

---

## 📦 Exemplos de Requisição

### Cadastrar medicamento
```http
POST /api/medicamentos/
Content-Type: application/json

{
  "nome": "Dipirona 500mg",
  "principio_ativo": "Dipirona Monoidratada",
  "fabricante": "EMS",
  "categoria": "Analgesico",
  "requer_receita": false,
  "preco": 8.90
}
```

### Registrar estoque inicial
```http
POST /api/estoque/
Content-Type: application/json

{
  "medicamento_id": 1,
  "quantidade": 100,
  "quantidade_minima": 20,
  "lote": "LOT2024001",
  "data_validade": "2026-12-31"
}
```

### Registrar saída de estoque
```http
PATCH /api/estoque/1/movimentar
Content-Type: application/json

{
  "tipo": "saida",
  "quantidade": 5
}
```

---

## 👨‍💻 Autor

[![GitHub](https://img.shields.io/badge/GitHub-LuizFilipe0207-181717?style=for-the-badge&logo=github)](https://github.com/LuizFilipe0207)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-luizfilipealvesalmeida-0077B5?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/luizfilipealvesalmeida)
