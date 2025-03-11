import os
import openai

# Carregar a chave da API do ambiente
openai.api_key = os.getenv('OPENAI_API_KEY')

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response)
except Exception as e:
    print(f"Erro: {e}")  