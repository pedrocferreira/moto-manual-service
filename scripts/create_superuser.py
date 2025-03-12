#!/usr/bin/env python
"""
Script para criar um superusuário sem interação.
Uso: python scripts/create_superuser.py
"""
import os
import sys
import django

# Configurar ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    django.setup()
    
    from django.contrib.auth import get_user_model
    from django.db.utils import IntegrityError
    
    User = get_user_model()
    
    # Configurações do superusuário - altere conforme necessário
    ADMIN_USERNAME = 'admin'
    ADMIN_EMAIL = 'admin@example.com'
    ADMIN_PASSWORD = 'admin123'  # Troque para uma senha mais segura em produção
    
    try:
        # Verifica se o usuário já existe
        if User.objects.filter(username=ADMIN_USERNAME).exists():
            print(f"Superusuário '{ADMIN_USERNAME}' já existe.")
            sys.exit(0)
            
        # Cria o superusuário
        User.objects.create_superuser(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD
        )
        print(f"Superusuário '{ADMIN_USERNAME}' criado com sucesso.")
        
    except IntegrityError:
        print(f"Erro: Não foi possível criar o superusuário '{ADMIN_USERNAME}'. Possivelmente já existe.")
    except Exception as e:
        print(f"Erro ao criar superusuário: {str(e)}")
        
except Exception as e:
    print(f"Erro ao configurar ambiente Django: {str(e)}") 