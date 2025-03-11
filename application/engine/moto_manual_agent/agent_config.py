import os
import dotenv
from rakam_systems.components.agents.agents import Agent, Action
from rakam_systems.components.agents.actions import RAGGeneration
from rakam_systems.components.vector_search.vector_store import VectorStore
from .prompts import MOTO_MANUAL_PROMPT
import logging
import time
from .response_cache import ResponseCache
from langdetect import detect

dotenv.load_dotenv()

MODEL = "gpt-3.5-turbo"
BASE_INDEX_PATH = "application/engine/moto_manual_agent/vector_indices"
MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_CONTEXT_LENGTH = 3000  # Aumentado para permitir mais contexto
RESPONSE_FORMAT_VERSION = "1.2"  # Atualizada versão do formato

# Prompt atualizado para incluir mais detalhes e especificações dos fabricantes
MOTO_MANUAL_SYS_PROMPT_WITH_REFS = """
Você é um mecânico especialista em motos, com vasto conhecimento técnico.
Sua função é fornecer instruções detalhadas e práticas sobre manutenção e reparo de motos,
usando as informações dos manuais técnicos disponíveis.

Regras:

1. Sempre forneça instruções passo a passo detalhadas
2. Para cada recomendação técnica, SEMPRE especifique:
   - Qual fabricante fez a recomendação
   - Em qual manual específico foi encontrada
   - A seção exata do manual
   - Qualquer número de referência ou código mencionado
   - Especificações técnicas exatas (medidas, torques, etc.)

3. Para informações sobre peças e materiais:
   - Especifique o fabricante recomendado
   - Liste códigos de peça quando disponíveis
   - Mencione alternativas aprovadas pelo fabricante
   - Inclua especificações técnicas detalhadas

4. Para procedimentos de manutenção:
   - Cite os intervalos recomendados por cada fabricante
   - Especifique condições especiais mencionadas
   - Inclua variações por modelo/ano quando relevante

5. Organize a resposta em seções:
   - Fonte da Informação (detalhando fabricante e manual)
   - Especificações Técnicas (com referências)
   - Ferramentas Necessárias (com códigos/especificações)
   - Precauções de Segurança
   - Procedimento Detalhado
   - Recomendações Adicionais do Fabricante
   - Referências Completas

6. Use linguagem clara e técnica
7. Se houver divergências entre fabricantes, cite todas as fontes e suas recomendações
8. Se uma informação específica não estiver disponível, indique claramente
"""

class MotoManualRAGAction(Action):
    def __init__(self, agent, **kwargs):
        super().__init__(agent, **kwargs)
        self.vector_store = VectorStore(
            base_index_path=BASE_INDEX_PATH,
            initialising=True
        )
        
        self._search_cache = {}
        self._max_cache_size = 1000
        
        self.rag_generator = RAGGeneration(
            agent=agent,
            sys_prompt=MOTO_MANUAL_SYS_PROMPT_WITH_REFS,
            prompt=MOTO_MANUAL_PROMPT,
            vector_stores=[self.vector_store],
            vs_descriptions=["Manuais técnicos de motocicletas"]
        )

        cache_dir = os.path.join(os.path.dirname(__file__), 'response_cache')
        self.response_cache = ResponseCache(cache_dir)
        self.clear_outdated_cache()

    def clear_outdated_cache(self):
        """Limpa o cache que não possui a versão atual do formato"""
        try:
            cache_dir = os.path.join(os.path.dirname(__file__), 'response_cache')
            if os.path.exists(cache_dir):
                for cache_file in os.listdir(cache_dir):
                    os.remove(os.path.join(cache_dir, cache_file))
            logging.info("Cache antigo limpo com sucesso")
        except Exception as e:
            logging.error(f"Erro ao limpar cache: {e}")

    def get_relevant_chunks(self, query, texts):
        """Encontra os chunks mais relevantes com contexto expandido"""
        relevant_chunks = []
        
        # Palavras-chave técnicas para busca expandida
        technical_keywords = [
            "especificação", "recomendação", "fabricante", "torque",
            "intervalo", "manutenção", "procedimento", "código",
            "peça", "ferramenta", "medida", "tolerância"
        ]
        
        # Expande a query com palavras-chave técnicas relevantes
        expanded_keywords = query.lower().split() + [
            kw for kw in technical_keywords
            if any(q in kw or kw in q for q in query.lower().split())
        ]
        
        for filename, text in texts:
            sections = text.split('\n\n')
            
            for i, section in enumerate(sections):
                section_lower = section.lower()
                
                # Verifica relevância expandida
                relevance_score = 0
                for keyword in expanded_keywords:
                    if keyword in section_lower:
                        relevance_score += 1
                        # Bonus para especificações técnicas
                        if any(tech_kw in section_lower for tech_kw in technical_keywords):
                            relevance_score += 0.5
                
                if relevance_score > 0:
                    # Captura contexto expandido
                    context = []
                    # Pega até 2 seções anteriores
                    start_idx = max(0, i - 2)
                    for j in range(start_idx, min(i + 3, len(sections))):
                        context.append(sections[j])
                    
                    relevant_chunks.append({
                        'source': filename,
                        'content': '\n\n'.join(context).strip(),
                        'relevance': relevance_score,
                        'section_index': i
                    })
        
        # Ordena por relevância e remove duplicatas próximas
        relevant_chunks.sort(key=lambda x: x['relevance'], reverse=True)
        filtered_chunks = []
        for chunk in relevant_chunks:
            if not any(
                abs(c['section_index'] - chunk['section_index']) < 3 
                and c['source'] == chunk['source']
                for c in filtered_chunks
            ):
                filtered_chunks.append(chunk)
        
        return filtered_chunks[:3]

    def execute(self, query: str, texts: list = None, **kwargs):
        try:
            # Detecta o idioma da query
            query_language = detect(query)
            
            # Define instruções específicas por idioma
            language_instructions = {
                'pt': 'Responda em português de forma clara e técnica.',
                'en': 'Answer in English clearly and technically.',
                'es': 'Responda en español de forma clara y técnica.',
                # Adicione outros idiomas conforme necessário
            }
            
            # Obtém a instrução no idioma detectado (usa inglês como fallback)
            language_instruction = language_instructions.get(query_language, language_instructions['en'])
            
            # Adiciona a instrução de idioma ao prompt
            query_with_instruction = f"{language_instruction}\n\nPergunta: {query}"
            
            logging.info("Executando a consulta: %s", query)
            
            relevant_chunks = self.get_relevant_chunks(query, texts) if texts else []
            
            context_parts = []
            for chunk in relevant_chunks:
                context_parts.append(f"""
                [Fonte: {chunk['source']}]
                {chunk['content']}
                """.strip())
            
            context = "\n\n---\n\n".join(context_parts)
            if len(context) > MAX_CONTEXT_LENGTH:
                context = context[:MAX_CONTEXT_LENGTH] + "..."
            
            response = self.rag_generator.execute(
                query=query_with_instruction,
                collection_names=["moto_manuals"],
                prompt_kwargs={"context": context} if context else {},
                stream=False,
                temperature=0.3,
                max_tokens=1000,  # Aumentado para respostas mais detalhadas
                top_p=0.85,
                presence_penalty=0.2
            )
            
            if response:
                sources_summary = f"\n\nReferências Detalhadas ({query_language}):\n"
                for chunk in relevant_chunks:
                    sources_summary += f"- Manual: {chunk['source']}\n"
                
                response = response + sources_summary
                
                self.response_cache.cache_response(
                    query, 
                    f"[Formato v{RESPONSE_FORMAT_VERSION}][Lang:{query_language}]\n{response}"
                )
            
            return response

        except Exception as e:
            # Mensagens de erro também no idioma detectado
            error_messages = {
                'pt': 'Desculpe, ocorreu um erro ao processar sua pergunta. Por favor, tente novamente.',
                'en': 'Sorry, an error occurred while processing your question. Please try again.',
                'es': 'Lo siento, ocurrió un error al procesar su pregunta. Por favor, inténtelo de nuevo.',
            }
            logging.error(f"Erro ao processar query: {str(e)}")
            return error_messages.get(query_language, error_messages['en'])

class MotoManualAgent(Agent):
    def __init__(self, model: str, api_key: str):
        super().__init__(model)
        self.actions = {
            "rag": MotoManualRAGAction(self)
        }

    def choose_action(self) -> Action:
        return self.actions["rag"]

AGENT = MotoManualAgent(
    model=MODEL,
    api_key=os.getenv("OPENAI_API_KEY")
)
