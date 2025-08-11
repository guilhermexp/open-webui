#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from open_webui.models.users import Users
from open_webui.utils.auth import create_token
from datetime import timedelta

# Buscar o usuário principal
user = Users.get_user_by_email("guilherme-varela@hotmail.com")

if user:
    print(f"Usuário encontrado: {user.name} ({user.email})")
    print(f"Role: {user.role}")
    print(f"ID: {user.id}")
    
    # Criar um novo token
    token = create_token(data={"id": user.id}, expires_delta=timedelta(days=30))
    
    print("\n" + "="*50)
    print("NOVO TOKEN GERADO:")
    print("="*50)
    print(token)
    print("="*50)
    
    print("\nPara usar este token:")
    print("1. Abra http://localhost:5173 no navegador")
    print("2. Abra o console do navegador (F12)")
    print("3. Execute o comando abaixo:")
    print(f"\nlocalStorage.setItem('token', '{token}');")
    print("\n4. Depois recarregue a página (F5)")
else:
    print("Usuário não encontrado!")