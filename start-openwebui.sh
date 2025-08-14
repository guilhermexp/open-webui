#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Open WebUI${NC}"

# Configurações
BACKEND_PORT="${BACKEND_PORT:-8082}"
FRONTEND_PORT="${FRONTEND_PORT:-5176}"

# Função para limpar processos
cleanup() {
    echo -e "\n${YELLOW}🛑 Parando todos os serviços...${NC}"
    
    # Parar processos filhos
    jobs -p | xargs -I {} kill {} 2>/dev/null
    
    exit 0
}

# Configurar trap para cleanup ao sair
trap cleanup EXIT INT TERM

# Verificar dependências
echo -e "${YELLOW}📋 Verificando dependências...${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm não encontrado. Instale Node.js primeiro${NC}"
    exit 1
fi

# Iniciar backend
echo -e "${GREEN}🔧 Iniciando backend na porta $BACKEND_PORT...${NC}"
cd backend
export CORS_ALLOW_ORIGIN="http://localhost:$FRONTEND_PORT"
export PORT=$BACKEND_PORT
uvicorn open_webui.main:app --host 0.0.0.0 --port $BACKEND_PORT --forwarded-allow-ips '*' --reload &
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
echo -e "\n${YELLOW}🔌 Para acessar MCP:${NC}"
echo -e "   1. Faça login como administrador"
echo -e "   2. Acesse Settings > Admin Settings > MCP"
echo -e "   3. Use 'My Connections' para gerenciar servidores MCP"
echo -e "   4. Use 'Browse Services' para descobrir novos serviços"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\n${YELLOW}💡 Pressione Ctrl+C para parar todos os serviços${NC}\n"

# Manter script rodando
wait