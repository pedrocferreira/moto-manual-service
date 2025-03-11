import os
import uuid
import fitz  # PyMuPDF
from typing import List, Dict, Any
from dataclasses import dataclass
from rakam_systems.components.vector_search.vector_store import VectorStore

@dataclass
class Metadata:
    """Classe para representar os metadados de um node."""
    node_id: str
    source: str
    chunk_id: int
    page: int
    source_file_uuid: str
    position: int
    custom: Dict[str, Any]  # Campo custom para metadados adicionais

@dataclass
class Node:
    """Classe para representar um node no vector store."""
    content: str
    metadata: Metadata

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrai texto de um arquivo PDF."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        print(f"  Número de páginas: {len(doc)}")
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            text += page_text
            if page_num < 3:  # Mostra as primeiras 3 páginas apenas
                print(f"  Página {page_num+1}: {len(page_text)} caracteres")
        if not text.strip():
            print("  AVISO: Nenhum texto extraído do PDF! Este PDF pode ser escaneado ou protegido.")
        return text
    except Exception as e:
        print(f"  ERRO ao processar {pdf_path}: {str(e)}")
        return ""

def process_manual(pdf_path: str) -> List[Node]:
    """Processa o manual e divide em chunks."""
    text = extract_text_from_pdf(pdf_path)
    
    # Aumenta o tamanho do chunk para capturar mais contexto
    chunk_size = 2000  # Aumentado de 1000 para 2000
    overlap = 200      # Adiciona sobreposição para manter contexto
    
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    
    # Gera um UUID único para o arquivo
    file_uuid = str(uuid.uuid4())
    
    # Formata os chunks como objetos Node
    formatted_chunks = []
    for i, chunk in enumerate(chunks):
        node_id = f"{os.path.basename(pdf_path)}_{i}"
        metadata = Metadata(
            node_id=node_id,
            source=os.path.basename(pdf_path),
            chunk_id=i,
            page=i // 2,  # Estimativa aproximada da página
            source_file_uuid=file_uuid,  # Mesmo UUID para todos os chunks do mesmo arquivo
            position=i,  # Usando o índice como posição
            custom={  # Adicionando metadados customizados
                "file_name": os.path.basename(pdf_path),
                "chunk_size": len(chunk),
                "total_chunks": len(chunks)
            }
        )
        node = Node(
            content=chunk,
            metadata=metadata
        )
        formatted_chunks.append(node)
    return formatted_chunks

def initialize_vector_store(manuals_dir: str) -> VectorStore:
    """Inicializa e popula o vector store com os manuais."""
    # Cria diretório para os índices se não existir
    index_dir = os.path.join(os.path.dirname(manuals_dir), 'vector_indices')
    os.makedirs(index_dir, exist_ok=True)
    
    # Inicializa o VectorStore com o diretório dos índices
    vector_store = VectorStore(base_index_path=index_dir)
    
    # Lista para armazenar todos os nodes
    all_nodes = []
    
    # Processa cada PDF na pasta de manuais
    for filename in os.listdir(manuals_dir):
        if filename.endswith('.pdf'):
            print(f"\nProcessando {filename}...")
            pdf_path = os.path.join(manuals_dir, filename)
            nodes = process_manual(pdf_path)
            all_nodes.extend(nodes)
            print(f"Extraídos {len(nodes)} chunks de {filename}")
    
    if all_nodes:
        print("\nCriando coleção com todos os chunks...")
        # Cria uma coleção com todos os nodes
        vector_store.create_collection_from_nodes(
            collection_name="moto_manuals",
            nodes=all_nodes
        )
        print(f"Total de {len(all_nodes)} chunks adicionados com sucesso!")
    
    return vector_store 