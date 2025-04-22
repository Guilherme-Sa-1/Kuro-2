import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader('https://ltafantasy.com/pt')
lista_documentos = loader.load
documento = ''
for doc in lista_documentos:
  documento = documento + doc.page_content



api_key = 'api-langchain'
os.environ['GROQ_API_KEY'] = api_key

chat = ChatGroq(model='llama-3.3-70b-versatile')


def resposta_do_bot(lista_mensagens):
  template = ChatPromptTemplate.from_messages(
      [('system', 'Você é um assistente amigável chamado Kuro')] +
      lista_mensagens
  )
  chain = template | chat
  return chain.invoke({}).content

print('Bem-vindo!Eu sou o Kuro, um chatbot criado pelo Gui! (Digite x se você quiser sair!)\n')
mensagens = []
while True:
  pergunta = input('Usuário: ')
  if pergunta.lower() == 'x':
    break
  mensagens.append(('user', pergunta))
  resposta = resposta_do_bot(mensagens)
  mensagens.append(('assistant', resposta))
  print(f'Bot: {resposta}')

print('\nAté logo!!')