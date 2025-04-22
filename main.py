import os

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader


def carregar_documento(url: str) -> str:
    """
    Faz o download das páginas em uma URL e concatena todo o conteúdo.
    """
    loader = WebBaseLoader(url)
    documentos = loader.load()  # lembre-se dos parênteses
    return "".join(doc.page_content for doc in documentos)


def criar_chat(api_key: str,
               model_name: str = "llama-3.3-70b-versatile") -> ChatGroq:
    """
    Configura a API key e retorna o cliente ChatGroq.
    """
    os.environ["GROQ_API_KEY"] = api_key
    return ChatGroq(model=model_name)


def resposta_do_bot(chat: ChatGroq,
                    lista_mensagens: list[tuple[str, str]]) -> str:
    """
    Constrói o prompt, invoca o modelo e retorna a resposta.
    """
    # system message fixa + histórico
    prompt = ChatPromptTemplate.from_messages(
        [("system", "Você é um assistente amigável chamado Kuro")]
        + lista_mensagens
    )
    chain = prompt | chat
    return chain.invoke({}).content


def main() -> None:
    # Carrega e guarda todo o conteúdo do site
    documento = carregar_documento("https://ltafantasy.com/pt")

    # Inicializa o chat com sua API key e modelo escolhido
    chat = criar_chat(api_key="api-langchain")

    print(
        "Bem‑vindo! Eu sou o Kuro, um chatbot criado pelo Gui!"
        " (Digite 'x' se quiser sair!)\n"
    )

    mensagens: list[tuple[str, str]] = []
    while True:
        pergunta = input("Usuário: ")
        if pergunta.lower() == "x":
            break

        mensagens.append(("user", pergunta))
        resposta = resposta_do_bot(chat, mensagens)
        mensagens.append(("assistant", resposta))

        print(f"Bot: {resposta}")

    print("\nAté logo!!")


if __name__ == "__main__":
    main()
