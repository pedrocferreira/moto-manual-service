# API de Consulta de Manuais de Motos

API REST em Django para consulta inteligente de manuais técnicos de motocicletas usando IA.

## Início Rápido

### Pré-requisitos
- Python 3.9
- Docker (opcional)
- PDFs dos manuais técnicos

### Instalação Rápida com Docker

```bash
# Clone o repositório
git clone [seu-repositorio]
cd [seu-projeto]

# Crie os diretórios necessários
mkdir -p application/engine/moto_manual_agent/manuals
mkdir -p application/engine/moto_manual_agent/vector_indices

# Adicione seus PDFs na pasta manuals/

# Construa e rode
docker build -t moto-manual-api .
docker run -p 8000:8000 moto-manual-api
```

### Instalação Local

```bash
# Crie e ative o ambiente virtual
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
pip install -e .

# Inicialize os índices
python scripts/initialize_indices.py

# Rode o servidor
python manage.py runserver
```

## Estrutura Básica

```
.
├── application/
│   └── engine/
│       └── moto_manual_agent/
│           ├── manuals/     # Seus PDFs aqui
│           └── vector_indices/
└── scripts/
```

## Uso Básico

```bash
# Exemplo de consulta
curl -X POST http://localhost:8000/api/consulta/ \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Como ajustar embreagem?"}'
```

## Dicas para Desenvolvimento

1. Mantenha os PDFs fora do git (já configurado no .gitignore)
2. Use branches para novas features
3. Faça commits pequenos e frequentes
4. Mantenha as dependências atualizadas

## Problemas Comuns

1. **Erro ao inicializar índices**: Verifique se há PDFs na pasta manuals/
2. **Erro de memória**: Reduza o tamanho dos PDFs ou ajuste as configurações
3. **Erro no Docker**: Verifique se os diretórios foram criados corretamente

## Links Úteis

- [Documentação Completa](docs/README.md)
- [Guia de Contribuição](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md) 