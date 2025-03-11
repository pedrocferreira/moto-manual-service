import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from application.engine.moto_manual_agent.utils import initialize_vector_store

def main():
    # Define o caminho para o diretório dos manuais
    manuals_dir = os.path.join(
        project_root,
        'application',
        'engine',
        'moto_manual_agent',
        'manuals'
    )
    
    print(f"Inicializando índices dos manuais em: {manuals_dir}")
    
    # Verifica se existem manuais
    if not os.path.exists(manuals_dir) or not os.listdir(manuals_dir):
        print("ERRO: Nenhum manual encontrado no diretório!")
        return
        
    try:
        # Inicializa o vector store
        vector_store = initialize_vector_store(manuals_dir)
        print("Índices inicializados com sucesso!")
    except Exception as e:
        print(f"ERRO ao inicializar índices: {str(e)}")

if __name__ == "__main__":
    main() 