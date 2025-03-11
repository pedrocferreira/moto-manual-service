import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .engine.moto_manual_agent.agent_config import AGENT
from scripts.setup_manuals import extract_text_from_pdfs
import os
from functools import lru_cache
import hashlib
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

logger = logging.getLogger(__name__)

# Defina o caminho para os manuais
manuals_dir = os.path.join(os.path.dirname(__file__), 'engine/moto_manual_agent/manuals')
logger.info(f"Caminho para os manuais: {manuals_dir}")

# Cache para textos processados
@lru_cache(maxsize=32)
def get_processed_texts(manuals_dir):
    return extract_text_from_pdfs(manuals_dir)

# Cache para queries similares
def get_query_hash(query):
    return hashlib.md5(query.lower().encode()).hexdigest()

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ask_manual(request):
    """
    Endpoint para fazer perguntas sobre os manuais de moto.
    """
    try:
        action = AGENT.choose_action()
        
        # Carrega VectorStore apenas uma vez
        if not hasattr(ask_manual, '_vector_store_loaded'):
            action.vector_store.load_vector_store()
            ask_manual._vector_store_loaded = True

        query = request.data.get("query")
        if not query:
            return Response({"error": "Query is required"}, status=400)
        
        # Usa cache para textos
        texts = get_processed_texts(manuals_dir)
        
        # Verifica cache para queries similares
        query_hash = get_query_hash(query)
        if hasattr(ask_manual, '_query_cache'):
            if query_hash in ask_manual._query_cache:
                return Response({
                    "answer": ask_manual._query_cache[query_hash],
                    "status": "success (cached)"
                })
        else:
            ask_manual._query_cache = {}

        response = action.execute(query=query, texts=texts)
        
        # Guarda no cache
        if len(ask_manual._query_cache) > 1000:  # Limita tamanho do cache
            ask_manual._query_cache.clear()
        ask_manual._query_cache[query_hash] = response
        
        return Response({
            "answer": response,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar query: {str(e)}", exc_info=True)
        return Response({
            "error": str(e),
            "status": "error"
        }, status=500)
