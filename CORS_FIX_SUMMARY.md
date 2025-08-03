# Correção de CORS para favicon.png

## Problema
O favicon.png está sendo carregado de http://localhost:8082/static/favicon.png mas está causando erro de CORS quando acessado de http://localhost:5173.

## Soluções aplicadas:

1. **Solução temporária**: 
   - Copiado favicon.png para /static/favicon.png
   - Configurado CORS_ALLOW_ORIGIN no .env

2. **Para aplicar a configuração CORS**:
   - Reiniciar o servidor backend para que o CORS_ALLOW_ORIGIN tenha efeito
   - O arquivo .env já foi atualizado com: CORS_ALLOW_ORIGIN=http://localhost:5173;http://localhost:5174

## Recomendação
Para uma correção definitiva, seria melhor usar caminhos relativos (/static/favicon.png) ao invés de URLs absolutas com o backend.
