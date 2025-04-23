import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders import PyPDFLoader

api_key = 'api-langchain'
os.environ['GROQ_API_KEY'] = api_key

chat = ChatGroq(model='llama-3.3-70b-versatile')


def resposta_bot(mensagens, documento):
  mensagem_system = '''Você é um assistente amigável chamado Kuro.
  Você utiliza as seguintes informações para formular as suas respostas: {informacoes}'''
  mensagens_modelo = [('system', mensagem_system)]
  mensagens_modelo += mensagens
  template = ChatPromptTemplate.from_messages(mensagens_modelo)
  chain = template | chat
  return chain.invoke({'informacoes': documento}).content

def carrega_site():
   url_site = input('Digite a URL do site: ')
   loader = WebBaseLoader(url_site)
   lista_documentos = loader.load()
   documento = ''
   for doc in lista_documentos:
    documento = documento + doc.page_content
   return documento

def carrega_pdf():
    caminho='arquivos/RoteiroViagemEgito.pdf'
    loader=PyPDFLoader(caminho)
    lista_documentos = loader.load()
    documento= ''
    for doc in lista_documentos:
        documento = documento+doc.page_content
    return documento

def carrega_youtube():
    url_youtube = input('Digite a URL do video: ')
    loader= YoutubeLoader.from_youtube_url(url_youtube,language=['pt'])
    lista_documentos = loader.load()
    documento= ''
    for doc in lista_documentos:
        documento = documento+doc.page_content
    return documento



print('Bem-vindo!Eu sou o Kuro, um chatbot criado pelo Gui! (Digite x se você quiser sair!)\n')

texto_selecao =print( '''Digite 1 se quiser conversar com um site
Digite 2 se quiser conversar com um pdf
Digite 3 se quiser conversar com um video do youtube
''')

while True:
    selecao = int(input())
    if selecao == 1:
        documento = carrega_site()
        break
    if selecao == 2:
        documento = carrega_pdf()
        break
    if selecao == 3:
        documento = carrega_youtube()
        break
    print('Digite um valor de 1 a 3')


mensagens = []
while True:
  pergunta = input('Usuario: ')
  if pergunta.lower() == 'x':
    break
  mensagens.append(('user', pergunta))
  resposta = resposta_bot(mensagens, documento)
  mensagens.append(('assistant', resposta))
  print(f'Kuro: {resposta}')
 

print('\nAté logo!!')