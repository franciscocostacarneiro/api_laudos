# 🚀 Production Deployment - Quick Start

Sua API está pronta para produção! Escolha uma das opções abaixo.

---

## ⚡ Render (Recomendado - mais simples)

### 5 minutos para colocar no ar

```bash
# 1. Vá para https://render.com
# 2. Clique: New → Web Service
# 3. Selecione seu repositório: api_laudos
# 4. Configure:
#    Name: api-laudos
#    Build Command: (deixar em branco)
#    Start Command: (deixar em branco)
# 5. Clique: Create Web Service
# 6. Vá em "Files" e faça upload de laudos_completos.xlsx
# 7. Adicione environment variable:
#    LAUDOS_DATA_FILE=/var/data/laudos_completos.xlsx
# 8. Clique: Deploy

# ✅ Pronto! API rodando em: https://api-laudos.onrender.com/docs
```

**Vantagens:**
- ✅ Fácil demais
- ✅ Grátis (com limitações)
- ✅ Auto-deploy no Git push
- ✅ Suporte bom

**Desvantagens:**
- ⚠️ Container hiberna se não tiver traffic
- ⚠️ Plano free tem limitações

📖 [Leia guia completo](./RENDER_DEPLOYMENT.md)

---

## 🚂 Railway (Alternativa legal)

### Igualmente simples

```bash
# 1. Vá para https://railway.app
# 2. Clique: New Project
# 3. Selecione "Deploy from GitHub repo"
# 4. Autorize e selecione api_laudos
# 5. Railway auto-detecta tudo
# 6. Adicione variáveis de ambiente
# 7. Configure volume para dados
# 8. Auto-deploy começa

# ✅ API rodando em: https://<seu-dominio>.railway.app/docs
```

**Vantagens:**
- ✅ Interface elegante
- ✅ Bom custo-benefício
- ✅ Multi-region
- ✅ PostgreSQL integrado

**Desvantagens:**
- ⚠️ Não tem free tier permanente
- ⚠️ Crédito inicial gasta em ~2 meses

📖 [Leia guia completo](./RAILWAY_DEPLOYMENT.md)

---

## 🐳 Docker Local / Self-Hosted

Se você quiser total controle:

```bash
# Build
docker build -t api_laudos .

# Run
docker run -p 8000:8000 \
  -v $(pwd)/laudos_completos.xlsx:/app/data/laudos_completos.xlsx \
  -e LAUDOS_DATA_FILE=/app/data/laudos_completos.xlsx \
  api_laudos

# Acesse: http://localhost:8000/docs
```

---

## 📋 Checklist Antes de Deployar

Tudo já está feito ✅, mas confirme:

- [ ] Repositório no GitHub
- [ ] `laudos_completos.xlsx` está .gitignored
- [ ] Tests passando localmente: `pytest tests/ -v`
- [ ] Docker builds sem erros: `docker build -t api_laudos .`
- [ ] Data file pronto para upload

📖 [Leia checklist completo](./DEPLOYMENT_CHECKLIST.md)

---

## 🔗 URLs Úteis Depois do Deploy

```
📚 Swagger UI:     https://seu-api.com/docs
📖 ReDoc:          https://seu-api.com/redoc
❤️ Health Check:   https://seu-api.com/health
📊 OpenAPI JSON:   https://seu-api.com/openapi.json
```

---

## 🛠 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| Deploy falha | Verifica logs do build, provavelmente erro no requirements.txt |
| API não inicia | Data file não encontrado - verifica path em LAUDOS_DATA_FILE |
| Lento demais | Excel grande em memória - plano pago ou migra para DB |
| 502 Bad Gateway | Container tá crashando - verifica logs |

---

## 📞 Próximos Passos

1. **Escolha plataforma** (Render recomendado)
2. **Deploy em 5-10 minutos**
3. **Teste endpoints** em `/docs`
4. **Configure domínio personalizado** (opcional)
5. **Monitore em produção** (logs, métricas)

---

## 🎯 Sua API está 100% pronta!

- ✅ 20 testes passando
- ✅ Documentação completa
- ✅ Docker pronto
- ✅ Guias de deployment
- ✅ CI/CD configurado
- ✅ Segurança OK

**Bora deployar? 🚀**

---

## 💡 Dica Final

Se for usar Render ou Railway, o mais fácil é:

1. Fazer git push para main
2. Ir no site da plataforma
3. Conectar repositório
4. Upload de dados
5. Clicar Deploy

Feito! 3 linhas de código rodando em produção 🎉
