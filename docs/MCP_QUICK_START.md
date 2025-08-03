# MCP Quick Start Guide

## 🚀 Início Rápido - Implementação MCP

### 1. Iniciar o Backend

**Terminal 1:**
```bash
cd backend
export CORS_ALLOW_ORIGIN=http://localhost:5175
python3 -m uvicorn open_webui.main:app --port 8082 --host 0.0.0.0 --reload
```

### 2. Frontend já está rodando!

O frontend já está rodando em http://localhost:5175

### 3. Executar Migração (se ainda não executada)

**Novo Terminal:**
```bash
cd backend

# Se estiver usando ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
python3 -m alembic upgrade head
```

### 4. Acessar MCP Settings

1. Acesse: http://localhost:5175
2. Faça login ou crie uma conta
3. Vá para: **Admin** → **Settings** → **MCP**

### 5. Adicionar um Servidor MCP de Teste

Clique em "Add Server" e use estas configurações:

**Opção 1 - Echo Server (teste simples):**
```
Name: Echo Test Server
Transport Type: Standard I/O
Command: python3
Arguments: 
  - -c
  - import sys; import json; print(json.dumps({"jsonrpc":"2.0","result":{"protocolVersion":"2024-11-05","capabilities":{},"serverInfo":{"name":"echo","version":"1.0.0"}},"id":"1"}))
```

**Opção 2 - File System (se tiver npx instalado):**
```
Name: File System
Transport Type: Standard I/O
Command: npx
Arguments:
  - @modelcontextprotocol/server-filesystem
  - /Users/guilhermevarela/Documents
```

### 6. Testar Conexão

1. Após adicionar, clique no ícone de check (✓) para testar
2. Se sucesso, clique nas setas circulares para sincronizar ferramentas
3. As ferramentas aparecerão no chat!

## 🎯 Verificação Rápida

✅ Backend rodando em http://localhost:8082  
✅ Frontend rodando em http://localhost:5175  
✅ Página MCP acessível em Settings  
✅ Pode adicionar e testar servidores  

## 🐛 Troubleshooting Rápido

**Erro de CORS:**
```bash
# Certifique-se de exportar antes de iniciar o backend
export CORS_ALLOW_ORIGIN=http://localhost:5175
```

**Erro de migração:**
```bash
cd backend
# Deletar banco se necessário
rm webui.db
# Recriar
python3 -m alembic upgrade head
```

**Porta em uso:**
```bash
# Matar processo na porta 8082
lsof -ti:8082 | xargs kill -9
```

---

Implementação MCP pronta para uso! 🎉