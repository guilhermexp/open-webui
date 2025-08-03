#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Open WebUI com servidores MCP${NC}"

# Configurações
BACKEND_PORT="${BACKEND_PORT:-8082}"
FRONTEND_PORT="${FRONTEND_PORT:-5176}"
MCP_PORT_1="${MCP_PORT_1:-8200}"
MCP_PORT_2="${MCP_PORT_2:-8201}"
MCP_API_KEY="${MCP_API_KEY:-dev-secret}"

# Função para limpar processos
cleanup() {
    echo -e "\n${YELLOW}🛑 Parando todos os serviços...${NC}"
    
    # Parar processos filhos
    jobs -p | xargs -I {} kill {} 2>/dev/null
    
    # Limpar portas MCP
    for port in $MCP_PORT_1 $MCP_PORT_2; do
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    done
    
    exit 0
}

# Configurar trap para cleanup ao sair
trap cleanup EXIT INT TERM

# Verificar dependências
echo -e "${YELLOW}📋 Verificando dependências...${NC}"

if ! command -v uvx &> /dev/null; then
    echo -e "${RED}❌ uvx não encontrado. Instale com: pip install uvx${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm não encontrado. Instale Node.js primeiro${NC}"
    exit 1
fi

# Criar pasta de trabalho para MCP
mkdir -p ~/mcp-workspace
echo "Arquivo de teste MCP" > ~/mcp-workspace/teste.txt

# Limpar processos antigos nas portas MCP
echo -e "${YELLOW}🧹 Limpando processos antigos...${NC}"
for port in $MCP_PORT_1 $MCP_PORT_2; do
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
done

# Aguardar portas liberarem
sleep 2

# Iniciar backend
echo -e "${GREEN}🔧 Iniciando backend na porta $BACKEND_PORT...${NC}"
cd backend
export CORS_ALLOW_ORIGIN=http://localhost:$FRONTEND_PORT
PORT=$BACKEND_PORT uvicorn open_webui.main:app --host 0.0.0.0 --forwarded-allow-ips '*' --reload &
BACKEND_PID=$!
cd ..

# Aguardar backend iniciar
echo -e "${YELLOW}⏳ Aguardando backend iniciar...${NC}"
sleep 5

# Verificar se backend está rodando
if ! curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend falhou ao iniciar${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Backend rodando!${NC}"

# Iniciar servidores MCP
echo -e "${GREEN}🔌 Iniciando servidores MCP...${NC}"

# Servidor de tempo
echo -e "${YELLOW}⏰ Iniciando servidor de tempo na porta $MCP_PORT_1...${NC}"
uvx mcpo --port $MCP_PORT_1 --api-key "$MCP_API_KEY" -- uvx mcp-server-time --local-timezone=America/Sao_Paulo &
MCP_PID_1=$!

# Servidor de memória
echo -e "${YELLOW}🧠 Iniciando servidor de memória na porta $MCP_PORT_2...${NC}"
uvx mcpo --port $MCP_PORT_2 --api-key "$MCP_API_KEY" -- npx -y @modelcontextprotocol/server-memory &
MCP_PID_2=$!

# Aguardar servidores MCP iniciarem
echo -e "${YELLOW}⏳ Aguardando servidores MCP iniciarem...${NC}"
sleep 10

# Verificar status dos servidores MCP
echo -e "${YELLOW}📊 Verificando servidores MCP...${NC}"
MCP_OK=true
for port in $MCP_PORT_1 $MCP_PORT_2; do
    if curl -s http://localhost:$port/docs > /dev/null 2>&1; then
        echo -e "${GREEN}✅ MCP porta $port: OK${NC}"
    else
        echo -e "${RED}❌ MCP porta $port: FALHA${NC}"
        MCP_OK=false
    fi
done

# Iniciar frontend
echo -e "${GREEN}🎨 Iniciando frontend na porta $FRONTEND_PORT...${NC}"
npm run dev -- --port $FRONTEND_PORT &
FRONTEND_PID=$!

# Aguardar frontend iniciar
echo -e "${YELLOW}⏳ Aguardando frontend iniciar...${NC}"
sleep 10

# Mostrar status final
echo -e "\n${GREEN}🎉 Sistema iniciado com sucesso!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📍 URLs disponíveis:${NC}"
echo -e "   Frontend: http://localhost:$FRONTEND_PORT"
echo -e "   Backend API: http://localhost:$BACKEND_PORT"
echo -e "   Backend Docs: http://localhost:$BACKEND_PORT/docs"

if [ "$MCP_OK" = true ]; then
    echo -e "\n${YELLOW}🔌 Servidores MCP:${NC}"
    echo -e "   Servidor de Tempo: http://localhost:$MCP_PORT_1/docs"
    echo -e "   Servidor de Memória: http://localhost:$MCP_PORT_2/docs"
    echo -e "\n${YELLOW}⚙️  Para configurar no Open WebUI:${NC}"
    echo -e "   1. Acesse Settings > Tools > Add Tool Server"
    echo -e "   2. Adicione as URLs dos servidores MCP"
    echo -e "   3. Use a API Key: $MCP_API_KEY"
fi

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\n${YELLOW}💡 Pressione Ctrl+C para parar todos os serviços${NC}\n"

# Manter script rodando
wait