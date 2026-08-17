import streamlit as st
import requests

st.title("📚 Study IA")
st.subheader("Bem vindo(a) ao StudyIA, como posso te ajudar?")

with st.sidebar:
    st.image("https://cdn.discordapp.com/attachments/1537323320771612765/1538726123528003674/pngegg.png?ex=6a83b9df&is=6a82685f&hm=ab95a41839bca4ed0253d570745d6a1d881f6cc33facf27e46991475ebf10b61&")
    st.info("Este aplicativo usa Inteligência Artificial para corrigir, resumir e traduzir seus textos de estudo em segundos.")

user_text = st.text_area("Cole seu texto aqui")

if st.button("Gerar"):
    if user_text:
        with st.spinner("Study IA está pensando..."):
            try:
                url = "https://studyia-zpmr.onrender.com/analisar-texto"
                dados = {"user_text": user_text}

                resposta_api = requests.post(url, json=dados)

                if resposta_api.status_code == 200:
                    resultado_json = resposta_api.json()
                    dados_resposta = resultado_json.get("resultado", {})
                    
                    if isinstance(dados_resposta, str):
                        resumo_txt = dados_resposta
                        portugues_txt = dados_resposta
                        ingles_txt = dados_resposta
                    else:
                        resumo_txt = dados_resposta.get("resumo", "")
                        portugues_txt = dados_resposta.get("portugues", "")
                        ingles_txt = dados_resposta.get("ingles", "")

                    st.success("Estudo gerado com sucesso!")
                    
                    # Abas exatamente como na última print
                    tab1, tab2, tab3 = st.tabs(["📋 Resumo", "🇧🇷 Português", "🇺🇸 English"])
                    
                    with tab1:
                        st.markdown("### Recapitulação (Pontos Essenciais)")
                        st.write(resumo_txt) # Mostra apenas os tópicos importantes na aba Resumo
                    with tab2:
                        st.markdown("### Versão completa e estruturada em português")
                        st.write(portugues_txt) # Mostra o texto detalhado e os erros ortográficos no final
                    with tab3:
                        st.markdown("### Tradução para inglês")
                        st.write(ingles_txt) # Mostra exclusivamente a versão traduzida para o inglês
                else:
                    st.error(f"StudyIA was unable to process your request. Status: {resposta_api.status_code}")

            except Exception as e:
                st.error(f"The StudyIA API is offline. Details: {e}")
    else:
        st.warning("Please enter some text first.")
