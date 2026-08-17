import json
from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="Minha API de Estudos com Groq")

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
    
    # Limita o texto do usuário caso seja grande demais para evitar estouro de tokens
    texto_usuario = pedido.user_text
    if len(texto_usuario) > 15000:
        texto_usuario = texto_usuario[:15000] + "\n[Texto cortado por excesso de tamanho...]"

    instrucao = (
        "You are an expert academic tutor. Analyze the user's text and return your response strictly as a JSON object with these three keys: 'resumo', 'portugues', and 'ingles'. "
        "CRITICAL JSON RULE: Do NOT use raw unescaped line breaks inside the string values. If you need a line break, you must use the escape sequence '\\n' or keep the text continuous. "
        "1. 'resumo': Crie um Guia de Estudo dividindo o texto em tópicos bem marcados usando emojis e títulos (ex: 📌 INTRODUÇÃO, 📌 CONTEXTO HISTÓRICO). Para cada tópico, cite o trecho do usuário usando (>) e logo abaixo escreva um parágrafo analítico e explicativo bem detalhado. "
        "2. 'portugues': Reescreva o texto do usuário de forma clara, altamente detalhada, fluida e expandida em português. "
        "3. 'ingles': Translate and deeply expand the Portuguese version into 100% professional, fluent, and academic English. No Portuguese or Spanish words.\n\n"
        f"Texto do usuário:\n{texto_usuario}"
    )
    
    try:
        # Busca os modelos e tenta priorizar um modelo robusto (como 70b ou mixtral) que suporte contextos maiores
        modelos_disponiveis = client.models.list()
        
        # Procura um modelo maior/mais estável primeiro, se não houver, pega o primeiro disponível
        modelo_selecionado = None
        for m in modelos_disponiveis.data:
            if "70b" in m.id or "mixtral" in m.id or "versatile" in m.id:
                modelo_selecionado = m.id
                break
        
        if not modelo_selecionado and modelos_disponiveis.data:
            modelo_selecionado = modelos_disponiveis.data[0].id
            
        response = client.chat.completions.create(
            model=modelo_selecionado,
            messages=[
                {"role": "system", "content": "You are a helpful academic assistant. Always output valid JSON with strict control characters handling."},
                {"role": "user", "content": instrucao}
            ],
            max_tokens=2048,  # Ajustado para um valor seguro e compatível
            temperature=0.3
        )
        
        content_str = response.choices[0].message.content.strip()
        
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
