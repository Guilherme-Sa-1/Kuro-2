import os

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader

# Carrega o conteúdo do site
loader = WebBaseLoader('https://ltafantasy.com/pt')
lista_documentos = loader.load()
documento = ''.join(doc.page_content for doc in lista_documentos)

# Configura a API key e inicializa o cliente Groq
api_key = 'api-langchain'
os.environ['GROQ_API_KEY'] = api_key
chat = ChatGroq(model='llama-3.3-70b-versatile')


def resposta_do_bot(lista_mensagens):
    """
    Constrói o prompt com histórico e invoca o modelo Groq, retornando o objeto de resposta.
    """
    template = ChatPromptTemplate.from_messages(
        [('system', 'Você é um assistente amigável chamado Kuro')] + lista_mensagens
    )
    chain = template | chat
    return chain.invoke({})


def main():
    print(
        "Bem-vindo! Eu sou o Kuro, um chatbot criado pelo Gui!"
        " (Digite 'x' se você quiser sair!)\n"
    )
    mensagens = []

    while True:
        pergunta = input('Usuário: ')
        if pergunta.lower() == 'x':
            break

        mensagens.append(('user', pergunta))
        resposta = resposta_do_bot(mensagens)
        mensagens.append(('assistant', resposta.content))

        # Exibe apenas o conteúdo da resposta
        print(resposta.content)

    print('\nAté logo!!')


if __name__ == '__main__':
    main()
