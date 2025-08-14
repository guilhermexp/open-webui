#!/bin/bash

# Script para iniciar Open WebUI com saída mínima
# Por padrão mostra apenas informações essenciais
# Use --verbose para ver toda a saída

VERBOSE=false
if [[ "$1" == "--verbose" ]]; then
    VERBOSE=true
fi

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Função para mostrar apenas se verbose
log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo "$1"
    fi
}

# Limpar portas
echo -e "${BLUE}🧹 Preparando ambiente...${NC}"
lsof -ti:8082 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# Backend
echo -e "${BLUE}🚀 Iniciando Backend...${NC}"
cd backend

if [ "$VERBOSE" = true ]; then
    source venv/bin/activate
    python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8082 --reload &
else
    source venv/bin/activate
    python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8082 --reload > /tmp/openwebui-backend.log 2>&1 &
fi
BACKEND_PID=$!

# Aguardar backend
echo -n "   Aguardando backend"
for i in {1..30}; do
    if curl -s http://localhost:8082/health > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Frontend
echo -e "${BLUE}🚀 Iniciando Frontend...${NC}"
cd ..

if [ "$VERBOSE" = true ]; then
    npm run dev &
else
    npm run dev > /tmp/openwebui-frontend.log 2>&1 &
fi
FRONTEND_PID=$!

# Aguardar frontend
echo -n "   Aguardando frontend"
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Resultado final
echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}✅ SISTEMA PRONTO!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "📍 Acesse:"
echo -e "   ${BLUE}Frontend:${NC} http://localhost:5173"
echo -e "   ${BLUE}API Docs:${NC} http://localhost:8082/docs"
echo ""
echo -e "📝 Logs salvos em:"
echo -e "   Backend:  /tmp/openwebui-backend.log"
echo -e "   Frontend: /tmp/openwebui-frontend.log"
echo ""
echo -e "💡 Comandos úteis:"
echo -e "   ${YELLOW}tail -f /tmp/openwebui-backend.log${NC}  # Ver logs do backend"
echo -e "   ${YELLOW}tail -f /tmp/openwebui-frontend.log${NC} # Ver logs do frontend"
echo -e "   ${YELLOW}./run-quiet.sh --verbose${NC}             # Modo verbose"
echo ""
echo -e "🛑 Pressione ${RED}Ctrl+C${NC} para parar"
echo -e "${GREEN}═══════════════════════════════════════${NC}"

# Função para limpar ao sair
cleanup() {
    echo -e "\n${YELLOW}⏹️  Parando serviços...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    lsof -ti:8082 | xargs kill -9 2>/dev/null
    lsof -ti:5173 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Serviços parados${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Manter script rodando
wait