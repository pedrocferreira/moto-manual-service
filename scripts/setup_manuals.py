import os
import sys
import PyPDF2
from sentence_transformers import SentenceTransformer
from rakam_systems.components.vector_search.vector_store import VectorStore
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed

# Adiciona o diretório raiz ao PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def extract_text_from_pdfs(pdf_folder):
    texts = []
    # Usar ProcessPoolExecutor para paralelizar a extração
    with ProcessPoolExecutor() as executor:
        pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
        futures = []
        
        for filename in pdf_files:
            file_path = os.path.join(pdf_folder, filename)
            future = executor.submit(process_single_pdf, file_path, filename)
            futures.append(future)
        
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    texts.append(result)
            except Exception as e:
                print(f"Erro ao processar PDF: {e}")
    
    return texts

def process_single_pdf(file_path, filename):
    try:
        # Adiciona cache de arquivo
        cache_path = file_path + '.cache'
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return (filename, f.read())
                
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + '\n'
            
            # Salva cache
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(text)
                
            return (filename, text)
    except Exception as e:
        print(f"Erro ao ler o PDF '{filename}': {e}")
        return None

def create_overlapping_chunks(text, chunk_size=800, overlap=100):
    """Chunks menores e com menos sobreposição para processamento mais rápido"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        if end > text_length:
            end = text_length
        
        chunk = text[start:end].strip()
        if len(chunk) > 50:  # Reduzido o tamanho mínimo
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks

def setup_manuals():
    try:
        # Cria diretório para manuais se não existir
        base_dir = os.path.join(
            os.path.dirname(__file__), 
            '../application/engine/moto_manual_agent'
        )
        manuals_dir = os.path.join(base_dir, 'manuals')
        indices_dir = os.path.join(base_dir, 'vector_indices')
        
        # Cria os diretórios necessários
        os.makedirs(manuals_dir, exist_ok=True)
        os.makedirs(indices_dir, exist_ok=True)
        
        print("\nDiretórios criados:")
        print(f"Manuais: {manuals_dir}")
        print(f"Índices: {indices_dir}\n")
        
        # Verifica se existem PDFs na pasta
        pdfs = [f for f in os.listdir(manuals_dir) if f.endswith('.pdf')]
        if not pdfs:
            print("\nNenhum arquivo PDF encontrado na pasta de manuais!")
            return
        
        print(f"\nEncontrados {len(pdfs)} arquivos PDF:")
        for pdf in pdfs:
            print(f"- {pdf}")
        
        # Extrai texto dos PDFs
        texts = extract_text_from_pdfs(manuals_dir)
        
        # Configuração otimizada do VectorStore
        vector_store = VectorStore(
            base_index_path=indices_dir,
            dimension=384,
            metric='cosine',
            nlist=100,  # Aumentado para melhor indexação
            nprobe=5,   # Aumentado para busca mais precisa
            cache_size=4096  # Aumentado o cache
        )
        
        print("\nProcessando todos os textos...")
        try:
            BATCH_SIZE = 500  # Reduzido para processamento mais rápido
            all_nodes = []
            
            for filename, text in texts:
                chunks = create_overlapping_chunks(text)
                
                # Cria índice de seções para busca mais rápida
                section_markers = {
                    "title": [],
                    "warning": [],
                    "important": []
                }
                
                nodes_batch = []
                for i, chunk in enumerate(chunks):
                    # Identifica seções importantes
                    chunk_lower = chunk.lower()
                    chunk_type = "content"
                    if any(marker in chunk_lower for marker in ["título", "capítulo", "seção"]):
                        chunk_type = "title"
                    elif any(marker in chunk_lower for marker in ["atenção", "aviso", "cuidado"]):
                        chunk_type = "warning"
                    
                    node = {
                        "content": chunk,
                        "id": f"{filename}-chunk-{i}",
                        "metadata": {
                            "source": filename,
                            "chunk_id": i,
                            "total_chunks": len(chunks),
                            "chunk_type": chunk_type
                        }
                    }
                    nodes_batch.append(node)
                    
                    if len(nodes_batch) >= BATCH_SIZE:
                        all_nodes.extend(nodes_batch)
                        nodes_batch = []
                
                if nodes_batch:
                    all_nodes.extend(nodes_batch)
            
            # Cria a coleção em lotes
            vector_store.create_collection_from_nodes(
                collection_name="moto_manuals",
                nodes=all_nodes,
                batch_size=BATCH_SIZE
            )
            
            print("Todos os textos foram processados e armazenados com sucesso!")
            
        except Exception as e:
            print(f"Erro ao processar os textos: {str(e)}")
        
        print("\nProcessamento concluído!")
        
    except TypeError as e:
        print(f"Erro na inicialização do VectorStore: {e}")
        logging.error(f"Erro na inicialização do VectorStore: {e}")
        return
    except Exception as e:
        print(f"Erro inesperado: {e}")
        logging.error(f"Erro inesperado: {e}")
        return

if __name__ == "__main__":
    setup_manuals() 