#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI simplificada
app = FastAPI(
    title="Notes App Backend",
    description="Backend simplificado para Notes App",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4174", "http://localhost:4173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Notes App Backend está funcionando!", "status": "ok"}

@app.get("/api/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy", "service": "notes-app-backend"}

@app.get("/api/status")
async def status():
    logger.info("Status endpoint accessed")
    return {
        "status": "running",
        "version": "1.0.0",
        "features": [
            "Editor avançado com chat integrado",
            "Sistema de transcrição de áudio",
            "Processamento de URLs",
            "Sistema de pastas organizadas"
        ]
    }

@app.on_event("startup")
async def startup_event():
    logger.info("Notes App Backend iniciado com sucesso na porta 8888")

if __name__ == "__main__":
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8888,
        reload=True,
        log_level="info"
    )
