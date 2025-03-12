import requests
import json
import sys

def login():
    login_url = "http://localhost:8000/api/login/"
    credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(login_url, json=credentials)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get('access')
    except Exception as e:
        print(f"Erro ao fazer login: {e}")
        return None

def test_query(query: str, token: str = None):
    url = "http://localhost:8000/ask-manual/"
    headers = {
        "Content-Type": "application/json"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    data = {
        "query": query
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("\nResposta:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"\nErro {response.status_code}:")
        print(response.text)

if __name__ == "__main__":
    token = login()
    if not token:
        print("Não foi possível obter o token de autenticação.")
        sys.exit(1)
    
    print(f"Autenticado com sucesso. Token: {token[:20]}...")
    
    while True:
        query = input("\nDigite sua pergunta (ou 'sair' para terminar): ")
        if query.lower() == 'sair':
            break
        test_query(query, token) 