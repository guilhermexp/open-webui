# MCP Testing Guide

## 🧪 Guia de Testes para Implementação MCP

Este guia fornece instruções passo a passo para testar a implementação MCP no Open WebUI.

## 📋 Pré-requisitos

1. **Python 3.11+** instalado
2. **Node.js 18+** instalado
3. **PostgreSQL** ou **SQLite** configurado
4. Dependências do backend instaladas:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
5. Dependências do frontend instaladas:
   ```bash
   npm install
   ```

## 🚀 Passos para Teste

### 1. Executar Migração do Banco de Dados

```bash
cd backend

# Para SQLite (padrão)
python -m alembic upgrade head

# OU se estiver usando ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
alembic upgrade head
```

### 2. Iniciar a Aplicação

#### Opção A: Usar o script de desenvolvimento (Recomendado)
```bash
# Na raiz do projeto
./dev.sh
```

#### Opção B: Iniciar manualmente

**Terminal 1 - Backend:**
```bash
cd backend
export CORS_ALLOW_ORIGIN=http://localhost:5173
python -m uvicorn open_webui.main:app --port 8082 --host 0.0.0.0 --reload
```

**Terminal 2 - Frontend:**
```bash
# Na raiz do projeto
npm run dev
```

### 3. Acessar a Aplicação

1. **Frontend**: http://localhost:5173
2. **Backend API Docs**: http://localhost:8082/docs
3. **Admin Panel**: http://localhost:5173/admin/settings
4. **MCP Settings**: http://localhost:5173/admin/settings/mcp

### 4. Testar Funcionalidade MCP

#### 4.1 Adicionar um Servidor MCP de Teste

1. Navegue até **Admin Settings → MCP**
2. Clique em **"Add Server"**
3. Configure um servidor de teste:

**Exemplo 1 - Servidor de Sistema de Arquivos:**
```
Name: File System Server
Transport Type: Standard I/O
Command: npx
Arguments: 
  - @modelcontextprotocol/server-filesystem
  - /path/to/allowed/directory
```

**Exemplo 2 - Servidor de Tempo (se instalado):**
```
Name: Time Server
Transport Type: Standard I/O
Command: uvx
Arguments:
  - mcp-server-time
```

#### 4.2 Testar Conexão

1. Após adicionar o servidor, clique no botão **"Test Connection"** (ícone de check)
2. Se bem-sucedido, você verá "Connection successful"

#### 4.3 Sincronizar Ferramentas

1. Clique no botão **"Sync Tools"** (ícone de setas circulares)
2. As ferramentas do servidor MCP serão importadas para o Open WebUI

#### 4.4 Usar as Ferramentas

1. Vá para uma conversa de chat
2. As ferramentas MCP aparecerão no seletor de ferramentas
3. Ative as ferramentas desejadas e use-as na conversa

## 🧪 Casos de Teste

### Teste 1: CRUD de Servidores
- [ ] Criar novo servidor MCP
- [ ] Editar servidor existente
- [ ] Desabilitar/habilitar servidor
- [ ] Deletar servidor

### Teste 2: Conexão e Sincronização
- [ ] Testar conexão com servidor stdio
- [ ] Sincronizar ferramentas
- [ ] Verificar se ferramentas aparecem no sistema

### Teste 3: Execução de Ferramentas
- [ ] Executar uma ferramenta MCP em chat
- [ ] Verificar resposta da ferramenta
- [ ] Testar com múltiplos parâmetros

### Teste 4: Gestão de Erros
- [ ] Tentar conectar a servidor inexistente
- [ ] Testar com comando inválido
- [ ] Verificar mensagens de erro

## 🐛 Troubleshooting

### Erro: "Migração falhou"
```bash
# Verifique se está no diretório correto
cd backend

# Se usando SQLite, delete o banco e recrie
rm webui.db
python -m alembic upgrade head
```

### Erro: "Cannot connect to MCP server"
1. Verifique se o comando do servidor está correto
2. Certifique-se de que o servidor MCP está instalado:
   ```bash
   # Para servidores npm
   npm install -g @modelcontextprotocol/server-filesystem
   
   # Para servidores Python
   pip install mcp-server-time
   ```

### Erro: "CORS error"
Certifique-se de que o backend foi iniciado com a variável CORS correta:
```bash
export CORS_ALLOW_ORIGIN=http://localhost:5173
```

## 📊 Verificação de Sucesso

A implementação está funcionando corretamente quando:

1. ✅ Você consegue acessar a página MCP em Admin Settings
2. ✅ Pode adicionar e editar servidores MCP
3. ✅ A conexão de teste retorna sucesso
4. ✅ As ferramentas são sincronizadas e aparecem no chat
5. ✅ As ferramentas podem ser executadas com sucesso

## 🎯 Próximos Passos

Após verificar que tudo funciona:

1. **Teste com diferentes servidores MCP**
2. **Configure servidores HTTP/WebSocket**
3. **Teste performance com múltiplos servidores**
4. **Documente casos de uso específicos**

---

**Última atualização**: 2025-08-01
**Versão**: 1.0.0