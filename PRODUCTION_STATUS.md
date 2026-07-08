# 🚀 API Em Produção - Replit

Sua API **API Laudos de Avaliação de Imóveis** está hospedada e funcionando!

---

## 📍 URL de Acesso

**API Base:** `https://api-laudos--chicoilha.replit.com`

### Endpoints Principais

```bash
# ❤️ Health Check
GET https://api-laudos--chicoilha.replit.com/health

# 📚 Swagger UI (Documentação interativa)
GET https://api-laudos--chicoilha.replit.com/docs

# 📖 ReDoc (Documentação estática)
GET https://api-laudos--chicoilha.replit.com/redoc

# 📋 Listar Laudos
GET https://api-laudos--chicoilha.replit.com/api/v1/laudos?page=1&pageSize=20

# 🔍 Buscar Laudo por ID
GET https://api-laudos--chicoilha.replit.com/api/v1/laudos/{laudoId}

# 📊 Estatísticas
GET https://api-laudos--chicoilha.replit.com/api/v1/laudos/stats
```

---

## 🧪 Testar a API

### 1. Via Swagger UI (Recomendado)
```
Abra no navegador:
https://api-laudos--chicoilha.replit.com/docs
```

### 2. Via Terminal
```bash
# Health check
curl https://api-laudos--chicoilha.replit.com/health

# Listar laudos
curl "https://api-laudos--chicoilha.replit.com/api/v1/laudos?categoria=Apartamento&pageSize=5"

# Estatísticas
curl "https://api-laudos--chicoilha.replit.com/api/v1/laudos/stats"
```

### 3. Via Python/Notebook
```python
import requests

# Health check
response = requests.get("https://api-laudos--chicoilha.replit.com/health")
print(response.json())

# Listar laudos
response = requests.get(
    "https://api-laudos--chicoilha.replit.com/api/v1/laudos",
    params={"categoria": "Apartamento", "pageSize": 10}
)
laudos = response.json()
print(f"Total de laudos: {laudos['totalItems']}")
```

---

## 📊 Dataset

- **Total de registros:** 189 laudos
- **Campos por laudo:** 145 atributos
- **Cobertura:** Brasil (todos os estados)
- **Período:** 2023-2024

---

## 🔍 Filtros Disponíveis

```bash
# Por categoria
?categoria=Apartamento
?categoria=Casa
?categoria=Lote

# Por valor
?valorMin=100000&valorMax=1000000

# Por área
?areaMin=50&areaMax=500

# Por período
?dataInicio=2023-01-01&dataFim=2024-12-31

# Por localização
?municipio=São Paulo
?bairro=Centro
?uf=SP

# Busca por texto
?q=Av+Paulista

# Paginação
?page=1&pageSize=20

# Ordenação
?sortBy=numeroLaudo&sortOrder=asc
```

---

## 💾 Próximos Passos

### 1. Monitorar em Produção
- Verificar logs do Replit regularmente
- Testar endpoints de tempos em tempos
- Documentar qualquer erro

### 2. Configurar Domínio Personalizado (Opcional)
```
Se quiser um domínio seu (ex: api.seudominio.com):
1. Configure DNS no Replit
2. Atualize esta documentação
```

### 3. Melhorias Futuras
- [ ] Adicionar autenticação (JWT)
- [ ] Implementar cache (Redis)
- [ ] Migrar Excel → PostgreSQL
- [ ] Adicionar rate limiting
- [ ] CI/CD pipeline (GitHub Actions)

### 4. Backups
- Faça backup regular de `laudos_completos.xlsx`
- Considere versionamento dos dados

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| API não responde | Verifique status do Replit, reinicie se necessário |
| Dados desatualizados | Atualize `laudos_completos.xlsx` no Replit |
| Resposta lenta | Dados em Excel em memória - considere migrar para DB |
| Erro 404 | Verifique se o endpoint está correto |

---

## 📚 Documentação Completa

Para mais detalhes sobre:
- **Estrutura da API:** Ver [README.md](./README.md)
- **Deployment:** Ver [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Schemas:** Ver [app/schemas.py](./app/schemas.py)
- **Testes:** Executar `pytest tests/ -v`

---

## 🔗 Links Úteis

- 🌐 GitHub Repository: https://github.com/franciscocostacarneiro/api_laudos
- 📚 Swagger UI: https://api-laudos--chicoilha.replit.com/docs
- 📖 ReDoc: https://api-laudos--chicoilha.replit.com/redoc
- 🐛 Report Issues: https://github.com/franciscocostacarneiro/api_laudos/issues

---

## 📞 Status da API

**Última atualização:** 2024-12-08  
**Status:** ✅ Online e funcionando  
**Hospedagem:** Replit  
**Domínio:** api-laudos--chicoilha.replit.com  

---

**Sua API está pronta para produção!** 🚀

Qualquer dúvida ou problema, consulte a documentação ou os logs do Replit.
