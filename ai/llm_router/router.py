"""
LLM Router - Zenith V1
Roteador para diferentes provedores de LLM (OpenAI, Anthropic, Claude)
"""

import os
import re
from typing import Dict, List, Optional, Any, Union

import httpx
import openai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Modelos
class QueryRequest(BaseModel):
    query: str
    user: Dict[str, Any]

class GenerateRequest(BaseModel):
    intent: str
    entities: List[str]
    data: Optional[Dict[str, Any]] = None
    user: Dict[str, Any]

class ProcessResponse(BaseModel):
    intent: str
    entities: List[str]
    provider: str
    raw_response: Optional[str] = None

class GenerateResponse(BaseModel):
    response: str
    intent: str
    entities: List[str]

# Configuração OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY", "")

# Configuração Anthropic
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# Provedores LLM
class LLMProviders:
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CLAUDE = "claude"  # Claude da Anthropic

# FastAPI app
app = FastAPI(title="Zenith LLM Router")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Funções para roteamento e processamento de LLM
async def route_to_llm(query: str, context: Dict = None) -> str:
    """Determina qual LLM deve ser usado com base na query."""
    # Default para OpenAI
    provider = LLMProviders.OPENAI
    
    # Lógica simples de roteamento baseada no tamanho da query e complexidade
    if len(query) > 1000:
        provider = LLMProviders.CLAUDE  # Claude lida melhor com contextos maiores
    elif "reasoning" in query.lower() or "explain" in query.lower():
        provider = LLMProviders.ANTHROPIC  # Anthropic pode ser melhor para raciocínio
    
    return provider

async def process_with_openai(query: str, context: Dict = None) -> str:
    """Processa a query usando OpenAI."""
    try:
        # Usando cliente da API diretamente
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant integrating with enterprise systems."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro com OpenAI: {str(e)}")

async def process_with_anthropic(query: str, context: Dict = None) -> str:
    """Processa a query usando Anthropic (Claude)."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ANTHROPIC_API_URL,
                json={
                    "model": "claude-2",
                    "prompt": f"\n\nHuman: {query}\n\nAssistant:",
                    "max_tokens_to_sample": 500,
                    "temperature": 0.7
                },
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": ANTHROPIC_API_KEY
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Erro com Anthropic API")
            
            return response.json().get("completion")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro com Anthropic: {str(e)}")

def extract_entities(query: str) -> List[str]:
    """Extrai entidades da query (simplificado para demo)."""
    # Em uma implementação real, seria usado NLP
    entities = []
    
    # Correspondência simples de palavras-chave
    if "sales" in query.lower() or "vendas" in query.lower():
        entities.append("sales")
    if "revenue" in query.lower() or "receita" in query.lower():
        entities.append("revenue")
    if "customer" in query.lower() or "cliente" in query.lower():
        entities.append("customer")
    if "product" in query.lower() or "produto" in query.lower():
        entities.append("product")
    
    return entities

# Rotas
@app.post("/process", response_model=ProcessResponse)
async def process_query(request: QueryRequest):
    try:
        query = request.query
        
        # Determinar qual LLM usar
        provider = await route_to_llm(query)
        
        # Processar com o provedor selecionado
        response = None
        if provider in [LLMProviders.OPENAI]:
            response = await process_with_openai(query)
        else:
            response = await process_with_anthropic(query)
        
        # Extrair intenção e entidades (em produção, seria mais sofisticado)
        # Para demo, usamos uma abordagem simples
        intent = "fetch_data" if "data" in query.lower() else "general_query"
        entities = extract_entities(query)
        
        return {
            "intent": intent,
            "entities": entities,
            "provider": provider,
            "raw_response": response
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar com LLM: {str(e)}")

@app.post("/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest):
    try:
        intent = request.intent
        entities = request.entities
        data = request.data
        
        # Construir prompt baseado na intenção, entidades e dados
        prompt = ""
        if intent == "fetch_data" and data:
            prompt = f"Baseado nos seguintes dados: {data}, forneça uma resposta útil abordando as entidades: {entities}"
        else:
            prompt = f"Forneça uma resposta útil sobre: {entities}"
        
        # Gerar resposta com OpenAI
        response = await process_with_openai(prompt)
        
        return {
            "response": response,
            "intent": intent,
            "entities": entities
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resposta: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"} 