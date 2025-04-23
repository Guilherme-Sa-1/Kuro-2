import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://ltafantasy.com/pt")
lista_documentos = loader.load()

documento = ''
for doc in lista_documentos:
  documento = documento + doc.page_content



api_key = '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'
os.environ['GROQ_API_KEY'] = api_key

chat = ChatGroq(model='llama-3.3-70b-versatile')

template = ChatPromptTemplate.from_messages([
    ('system', 'Você é um assistente amigável chamado Asimo e tem acesso as seguinte informações para dar as suas respostas: {documentos_informados}'),
    ('user', '{input}')
])

chain = template | chat
resposta = chain.invoke({'documentos_informados': documento, 'input': 'O que pode me dizer sobre o site que dei para o scrapping?'})

print(resposta.content)