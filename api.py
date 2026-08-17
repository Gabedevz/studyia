import json
from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="Minha API de Estudos com Groq")

# Dica de segurança: considere usar variáveis de ambiente no futuro 
# em vez de deixar a chave exposta diretamente no código!
client = Groq(api_key="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")

class Pedidotexto(BaseModel):
    user_text: str

@app.get("/")
def read_root():
    return {"status": "online", "message": "API rodando! Use o endpoint /analisar-texto"}

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
        # Busca automaticamente o primeiro modelo disponível na sua conta
        modelos_disponiveis = client.models.list()
        # Filtramos modelos que suportam chat (chat-completions)
        modelo_selecionado = [m.id for m in modelos_disponiveis.data if "chat" in m.id or "llama" in m.id or "mixtral" in m.id][0]
        
        response = client.chat.completions.create(
            model=modelo_selecionado,
            messages=[
                {"role": "system", "content": "You are a helpful academic assistant. Always output valid JSON with strict control characters handling."},
                {"role": "user", "content": instrucao}
            ],
            max_tokens=4000,
            temperature=0.3
        )
        
        content_str = response.choices[0].message.content.strip()
        
        # Limpeza básica do JSON
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
