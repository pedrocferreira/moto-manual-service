import requests
import json

def test_query(query: str):
    url = "http://localhost:8000/ask-manual/"
    headers = {
        "Content-Type": "application/json"
    }
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
    while True:
        query = input("\nDigite sua pergunta (ou 'sair' para terminar): ")
        if query.lower() == 'sair':
            break
        test_query(query) 