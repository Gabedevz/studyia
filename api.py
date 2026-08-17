import json
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

app = FastAPI(title="Minha API de Estudos com Gemini")

# Insira aqui a sua chave da API do Google AI Studio (gratuita)
client = genai.Client(api_key="AQ.Ab8RN6JgeISolLnSz_H_etfzO4aSVJvU-vfm07G3b1Ye259r5Q")

class Pedidotexto(BaseModel):
    user_text: str

@app.get("/")
def read_root():
    return {"status": "online", "message": "API rodando com Gemini! Use o endpoint /analisar-texto"}

@app.post("/analisar-texto")
@app.get("/analisar-texto")
def analisar_texto(pedido: Pedidotexto = None):
    if pedido is None or not pedido.user_text:
        return {"status": "online", "mensagem": "A API está funcionando! Envie um POST com o texto para analisar."}
    
    instrucao = (
        "You are an expert academic tutor. Analyze the user's text and return your response strictly as a JSON object with these three keys: 'resumo', 'portugues', and 'ingles'. "
        "CRITICAL JSON RULE: Do NOT use raw unescaped line breaks inside the string values. If you need a line break, you must use the escape sequence '\\n' or keep the text continuous. "
        "1. 'resumo': Crie um Guia de Estudo dividindo o texto em tópicos bem marcados usando emojis e títulos (ex: 📌 INTRODUÇÃO, 📌 CONTEXTO HISTÓRICO). Para cada tópico, cite o trecho do usuário usando (>) e logo abaixo escreva um parágrafo analítico e explicativo bem detalhado. "
        "2. 'portugues': Reescreva o texto do usuário de forma clara, altamente detalhada, fluida e expandida em português. "
        "3. 'ingles': Translate and deeply expand the Portuguese version into 100% professional, fluent, and academic English. No Portuguese or Spanish words.\n\n"
        f"Texto do usuário:\n{pedido.user_text}"
    )
    
    try:
        # Utiliza o Gemini Flash, que é extremamente rápido e robusto para textos longos
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=instrucao,
        )
        
        content_str = response.text.strip()
        
        # Limpeza de blocos de código caso o modelo retorne marcação markdown
        if content_str.startswith("```json"):
            content_str = content_str[7:]
        if content_str.startswith("```"):
            content_str = content_str[3:]
        if content_str.endswith("```"):
            content_str = content_str[:-3]
            
        conteudo_ia = json.loads(content_str.strip(), strict=False)
        return {"resultado": conteudo_ia}
        
    except Exception as e:
        erro_msg = f"Erro ao processar a requisição: {str(e)}"
        return {"resultado": {"resumo": erro_msg, "portugues": erro_msg, "ingles": erro_msg}}
