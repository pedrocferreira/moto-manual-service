import os
import dotenv
from rakam_systems.components.agents.agents import Agent, Action
from rakam_systems.components.agents.actions import RAGGeneration
from rakam_systems.components.vector_search.vector_store import VectorStore
from .prompts import MOTO_MANUAL_PROMPT, LANGUAGE_PROMPTS
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
            logging.info("Iniciando execução da consulta")
            
            # Detecta o idioma da query
            query_language = detect(query)
            logging.info(f"Idioma detectado: {query_language}")
            
            # Define idiomas suportados - se não for suportado, usa inglês
            supported_languages = ['pt', 'en', 'es', 'fr', 'de', 'it']
            if query_language not in supported_languages:
                logging.info(f"Idioma {query_language} não suportado, usando inglês como padrão")
                query_language = 'en'
            
            logging.info("Configurando instruções para o idioma")
            
            # Define instruções específicas por idioma
            language_instructions = {
                'pt': 'Responda em português brasileiro de forma clara e técnica.',
                'en': 'Answer in English clearly and technically.',
                'es': 'Responda en español de forma clara y técnica.',
                'fr': 'Répondez en français de manière claire et technique.',
                'de': 'Antworten Sie klar und technisch auf Deutsch.',
                'it': 'Rispondi in italiano in modo chiaro e tecnico.',
            }
            
            # Obter a instrução no idioma correto
            language_instruction = language_instructions.get(query_language, language_instructions['en'])
            query_with_instruction = f"{language_instruction}\n\nPergunta: {query}"
            logging.info(f"Query formatada: {query_with_instruction[:50]}...")
            
            # Processar contexto
            logging.info("Processando chunks de contexto")
            relevant_chunks = self.get_relevant_chunks(query, texts) if texts else []
            logging.info(f"Encontrados {len(relevant_chunks)} chunks relevantes")
            
            context_parts = []
            for chunk in relevant_chunks:
                context_parts.append(f"""
                [Fonte: {chunk['source']}]
                {chunk['content']}
                """.strip())
            
            context = "\n\n---\n\n".join(context_parts)
            if len(context) > MAX_CONTEXT_LENGTH:
                context = context[:MAX_CONTEXT_LENGTH] + "..."
            
            # Preparar prompt do sistema
            logging.info("Preparando prompt do sistema")
            try:
                language_specific_prompt = LANGUAGE_PROMPTS[query_language]['system_prompt'] if query_language in LANGUAGE_PROMPTS else LANGUAGE_PROMPTS['en']['system_prompt']
                logging.info(f"Prompt do sistema obtido para idioma {query_language}")
            except Exception as prompt_error:
                logging.error(f"Erro ao obter prompt específico: {prompt_error}")
                # Fallback para o prompt original em caso de erro
                language_specific_prompt = MOTO_MANUAL_SYS_PROMPT_WITH_REFS
            
            # Chamada à API
            logging.info("Enviando requisição para o modelo de linguagem")
            try:
                response = self.rag_generator.execute(
                    query=query_with_instruction,
                    collection_names=["moto_manuals"],
                    prompt_kwargs={"context": context} if context else {},
                    stream=False,
                    temperature=0.3,
                    max_tokens=1000,
                    top_p=0.85,
                    presence_penalty=0.2,
                    sys_prompt=language_specific_prompt
                )
                logging.info("Resposta recebida do modelo")
            except Exception as api_error:
                logging.error(f"Erro na chamada à API: {api_error}")
                raise
            
            # Processamento da resposta
            if response:
                logging.info("Formatando resposta final")
                # Adiciona as referências no idioma correto
                ref_label = "Detailed References:" if query_language == 'en' else "Referências Detalhadas:"
                sources_summary = f"\n\n{ref_label}\n"
                for chunk in relevant_chunks:
                    sources_summary += f"- Manual: {chunk['source']}\n"
                
                response = response + sources_summary
                
                # Registra o idioma no cache
                self.response_cache.cache_response(
                    query, 
                    f"[Formato v{RESPONSE_FORMAT_VERSION}][Lang:{query_language}]\n{response}"
                )
            
            return response

        except Exception as e:
            logging.error(f"Erro detalhado: {str(e)}", exc_info=True)
            # Mensagens de erro traduzidas
            error_messages = {
                'pt': 'Desculpe, ocorreu um erro ao processar sua pergunta. Por favor, tente novamente.',
                'en': 'Sorry, an error occurred while processing your question. Please try again.',
                'es': 'Lo siento, ocurrió un error al procesar su pregunta. Por favor, inténtelo de nuevo.',
                'fr': 'Désolé, une erreur s\'est produite lors du traitement de votre question. Veuillez réessayer.',
                'de': 'Entschuldigung, bei der Verarbeitung Ihrer Frage ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.',
                'it': 'Mi dispiace, si è verificato un errore durante l\'elaborazione della tua domanda. Per favore riprova.',
            }
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

# Adapte o prompt do sistema para ser mais explícito sobre o idioma
def get_system_prompt_with_language(language_code):
    # Base do prompt em inglês
    base_prompt = """
    You are a motorcycle mechanic expert with extensive technical knowledge.
    Your role is to provide detailed and practical instructions on motorcycle maintenance and repair,
    using information from available technical manuals.
    
    Rules:
    
    1. Always provide detailed step-by-step instructions
    2. For each technical recommendation, ALWAYS specify:
       - Which manufacturer made the recommendation
       - In which specific manual it was found
       - The exact section of the manual
       - Any reference numbers or codes mentioned
       - Exact technical specifications (measurements, torques, etc.)
    """
    
    # Adicione instruções explícitas sobre o idioma
    language_specific = {
        'pt': "\nIMPORTANTE: Responda SEMPRE em português brasileiro, independentemente do idioma usado nos manuais técnicos.",
        'en': "\nIMPORTANT: ALWAYS answer in English, regardless of the language used in the technical manuals.",
        'es': "\nIMPORTANTE: Responda SIEMPRE en español, independientemente del idioma utilizado en los manuales técnicos.",
        'fr': "\nIMPORTANT: Répondez TOUJOURS en français, quel que soit la langue utilisée dans les manuels techniques.",
        'de': "\nWICHTIG: Antworten Sie IMMER auf Deutsch, unabhängig von der in den technischen Handbüchern verwendeten Sprache.",
        'it': "\nIMPORTANTE: Rispondi SEMPRE in italiano, indipendentemente dalla lingua utilizzata nei manuali tecnici.",
    }
    
    return base_prompt + language_specific.get(language_code, language_specific['en']) + MOTO_MANUAL_SYS_PROMPT_WITH_REFS
