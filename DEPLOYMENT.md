# API Laudos de Avaliação de Imóveis CEF 🏠

## Overview

REST API em FastAPI para consultar e filtrar laudos de avaliação de imóveis da Caixa Econômica Federal (CEF). Documentação automática via Swagger UI e ReDoc.

**Status:** ✅ Produção-ready | 20/20 testes passando | OpenAPI 3.1

---

## 📦 Quick Start Local

### Pré-requisitos
- Python 3.11+
- Git

### Instalação (5 min)

```bash
# 1. Clone o repositório
git clone https://github.com/franciscocostacarneiro/api_laudos.git
cd api_laudos

# 2. Crie um virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Execute o servidor
python -m uvicorn app.main:app --reload
```

**API rodando em:** http://127.0.0.1:8000
- 📚 Swagger UI: http://127.0.0.1:8000/docs
- 📖 ReDoc: http://127.0.0.1:8000/redoc

---

## 🐳 Docker (Local)

```bash
# Build e execute com docker-compose
docker-compose up --build

# Ou apenas com Docker
docker build -t api_laudos .
docker run -p 8000:8000 -v $(pwd)/laudos_completos.xlsx:/app/data/laudos_completos.xlsx:ro api_laudos
```

---

## 🚀 Deployment em Produção

### Opção 1: **Render** (Recomendado - Free tier)

#### Passo 1: Preparar o repositório (já feito ✅)
- ✅ `.gitignore` - exclui `laudos_completos.xlsx`
- ✅ `render.yaml` - configuração de deploy
- ✅ `Dockerfile` - imagem de produção
- ✅ `requirements.txt` - dependências

#### Passo 2: Conectar no Render
1. Vá para https://render.com
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub
4. Configure:
   ```
   Name: api_laudos
   Runtime: Docker
   Build Command: (deixar em branco - usa Dockerfile)
   Start Command: (deixar em branco - usa Dockerfile)
   ```

#### Passo 3: Upload dos dados
1. Na dashboard do Render, abra a web service
2. Vá em **"Files"**
3. Faça upload de `laudos_completos.xlsx`
4. Configure a variável de ambiente:
   ```
   LAUDOS_DATA_FILE = /var/data/laudos_completos.xlsx
   ```

#### Passo 4: Deploy
- Clique em **"Deploy"**
- Aguarde ~5 minutos
- API estará em: `https://api-laudos.onrender.com`

---

### Opção 2: **Railway** (Alternativa)

#### Passo 1-2: Conectar no Railway
1. Vá para https://railway.app
2. Clique em **"New Project"** → **"Deploy from GitHub repo"**
3. Selecione seu repositório

#### Passo 3: Configurar variáveis
```
PYTHONUNBUFFERED=1
PORT=8000
LAUDOS_DATA_FILE=/data/laudos_completos.xlsx
```

#### Passo 4: Upload de dados
- Configure um volume para o arquivo Excel, ou
- Use uma URL pública em S3

Railway iniciará automaticamente o deploy!

---

### Opção 3: **Fly.io** (VPS melhor)

```bash
# 1. Instale o CLI
curl -L https://fly.io/install.sh | sh

# 2. Faça login
flyctl auth login

# 3. Crie o app
flyctl launch

# 4. Configure variáveis
flyctl secrets set LAUDOS_DATA_FILE=/data/laudos_completos.xlsx

# 5. Deploy
flyctl deploy
```

---

### Opção 4: **AWS / Google Cloud / Azure**

Veja [DEPLOYMENT_ADVANCED.md](./DEPLOYMENT_ADVANCED.md) para instruções detalhadas (ECS, Cloud Run, App Service).

---

## 📡 Endpoints

### Health Check
```bash
GET /health
# Response: {"status": "ok", "version": "1.0.0", "reportsLoaded": 189}
```

### Listar Laudos
```bash
GET /api/v1/laudos
  ?page=1
  &pageSize=20
  &sortBy=numeroLaudo
  &sortOrder=asc
  &categoria=Apartamento
  &municipio=São Paulo
  &bairro=Centro
  &grupoLaudo=RESIDENCIAL
  &valorMin=100000
  &valorMax=1000000
  &areaMin=50
  &areaMax=500
  &dataInicio=2023-01-01
  &dataFim=2024-12-31
  &q=Av%20Paulista
```

**Response:**
```json
{
  "data": [
    {
      "numeroLaudo": "123456",
      "versaoLaudo": "01",
      "grupoLaudo": "RESIDENCIAL",
      "locationInfo": { "categoriaImovel": "Apartamento", ... },
      "valuationInfo": { "metodo": "...", "area": 150, ... }
    }
  ],
  "page": 1,
  "pageSize": 20,
  "totalItems": 189,
  "totalPages": 10
}
```

### Obter um Laudo
```bash
GET /api/v1/laudos/{laudoId}
```

**Response:** Laudo completo com todos os detalhes.

### Estatísticas
```bash
GET /api/v1/laudos/stats?categoria=Apartamento&municipio=São Paulo
```

**Response:**
```json
{
  "totalCount": 45,
  "categories": [
    { "categoria": "Apartamento", "count": 45, "avgValor": 350000 }
  ],
  "municipios": [
    { "municipio": "São Paulo", "count": 45, "avgValor": 350000 }
  ]
}
```

---

## 🧪 Testes

```bash
# Executar suite de testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=app

# Resultado esperado: 20/20 testes passando ✅
```

---

## 📊 Dataset

- **Total de registros:** 189 laudos
- **Campos:** 145 atributos por laudo
- **Cobertura:** Brasil (todos os estados)
- **Período:** 2023-2024
- **Tamanho:** ~177 KB (Excel)

### Estrutura de dados

Cada laudo contém:
- **Básico:** Número, versão, grupo, tipo
- **Imóvel:** Categoria, localização (endereço, bairro, município, UF)
- **Geolocalização:** Coordenadas (latitude/longitude)
- **Avaliação:** Método, valor (individual e comercial), área
- **Signatários:** Engenheiro responsável, empresa

---

## 🛠 Arquitetura

```
app/
├── main.py              # FastAPI app + lifespan + health check
├── schemas.py           # Pydantic schemas (contract)
├── api/
│   └── laudos.py        # Endpoints /api/v1/laudos/*
└── core/
    ├── config.py        # Settings (env-driven)
    ├── data.py          # In-memory store + filtering
    └── errors.py        # Unified error handling

tests/
└── test_api.py          # 20 testes (100% passing)

Dockerfile              # Multi-stage build para produção
docker-compose.yml      # Dev environment
render.yaml            # Deploy config (Render)
railway.json           # Deploy config (Railway)
gunicorn.conf.py       # Production ASGI server
requirements.txt       # Dependências Python
```

---

## 🔒 Segurança

- ✅ `.gitignore` - dados sensíveis não são commitados
- ✅ `LAUDOS_DATA_FILE` env var - configurável por servidor
- ✅ Type hints + Pydantic validation - validação em runtime
- ✅ CORS desabilitado (adicione se necessário)
- ✅ Rate limiting (implemente se necessário com slowapi)
- ✅ Health checks - monitoramento em produção

---

## 📝 Documentação

- **Swagger UI:** `/docs` - interface interativa
- **ReDoc:** `/redoc` - documentação estática
- **OpenAPI Schema:** `/openapi.json` - machine-readable

---

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/sua-feature`)
3. Commit suas mudanças (`git commit -am 'Add feature'`)
4. Push para a branch (`git push origin feature/sua-feature`)
5. Abra um Pull Request

---

## 📄 Licença

MIT License - veja [LICENSE](./LICENSE) para detalhes.

---

## 👤 Autor

Francisco Costa Carneiro  
GitHub: [@franciscocostacarneiro](https://github.com/franciscocostacarneiro)

---

## 📞 Suporte

- 🐛 Issues: [GitHub Issues](https://github.com/franciscocostacarneiro/api_laudos/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/franciscocostacarneiro/api_laudos/discussions)

---

## 🚀 Próximos passos

- [ ] Adicionar autenticação (JWT)
- [ ] Implementar rate limiting
- [ ] Cache com Redis
- [ ] CI/CD com GitHub Actions
- [ ] Monitoramento com Sentry
- [ ] Database (PostgreSQL) em vez de Excel
