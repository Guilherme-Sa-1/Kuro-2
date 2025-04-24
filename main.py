from flask import Flask, request, render_template_string, redirect, url_for
from dotenv import load_dotenv
import os
from uuid import uuid4
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader, YoutubeLoader, PyPDFLoader

# Carrega variáveis de ambiente do .env
def load_env():
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise RuntimeError("GROQ_API_KEY não encontrada. Verifique o .env.")
    os.environ['GROQ_API_KEY'] = api_key
    return api_key

# Inicialização
api_key = load_env()
chat = ChatGroq(groq_api_key=api_key, model='llama3-70b-8192')
app = Flask(__name__)

# Estrutura das conversas: id -> {'name': str, 'history': [(role, text)], 'context': str}
global_conversations = {}

# Carregadores
def load_site(url: str) -> str:
    docs = WebBaseLoader(url).load()
    return ''.join(d.page_content for d in docs)

def load_pdf(path: str) -> str:
    docs = PyPDFLoader(path).load()
    return ''.join(d.page_content for d in docs)

def load_youtube(url: str) -> str:
    docs = YoutubeLoader.from_youtube_url(url, language=['pt']).load()
    return ''.join(d.page_content for d in docs)

# Função de resposta
def resposta_bot(history: list, contexto: str) -> str:
    system_msg = (
        "Você é um assistente amigável chamado Kuro. "
        "Use as informações abaixo para responder ao usuário: {informacoes}"
    )
    messages = [('system', system_msg)] + history
    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | chat
    return chain.invoke({'informacoes': contexto}).content

# Template HTML
HTML_TEMPLATE = '''
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Chatbot Kuro</title>
  <style>
    body { margin:0; padding:0; height:100vh; display:flex; font-family:Arial,sans-serif; background:#0f1115; color:#fff; }
    .sidebar { width:260px; background:#111; overflow-y:auto; }
    .sidebar h2 { margin:0; padding:1rem; text-align:center; border-bottom:1px solid #333; }
    .sidebar ul { list-style:none; margin:0; padding:0; }
    .sidebar li { display:flex; align-items:center; justify-content:space-between; padding:0.5rem 1rem; }
    .sidebar li.active { background:#333; }
    .sidebar a { color:inherit; text-decoration:none; flex:1; }
    .sidebar button { background:transparent; border:none; color:#888; cursor:pointer; }
    .main { flex:1; display:flex; flex-direction:column; }
    .main-header { background:#111; padding:1rem; text-align:center; border-bottom:1px solid #333; }
    .load-form, .input-area { display:flex; padding:0.75rem; gap:0.5rem; }
    .load-form input, .input-area input { flex:1; padding:0.75rem 1rem; border-radius:999px; border:none; background:#202226; color:#fff; }
    .load-form button, .input-area button { padding:0.75rem 1.5rem; border-radius:999px; border:none; background:#007bff; color:#fff; cursor:pointer; }
    .load-form button:hover, .input-area button:hover { opacity:0.9; }
    .source-selection { text-align:center; margin-top:0.5rem; }
    .messages { flex:1; overflow-y:auto; padding:1rem; display:flex; flex-direction:column; gap:1rem; }
    .message { max-width:75%; padding:0.75rem 1rem; border-radius:1rem; color:#fff; word-wrap:break-word; }
    .message.user { align-self:flex-end; background:#0056b3; }
    .message.assistant { align-self:flex-start; background:#1f5d3b; }
  </style>
</head>
<body>
  <div class="sidebar">
    <h2>Conversas</h2>
    <ul>
      <li><a href="?new=1">+ Nova</a></li>
      {% for cid, conv in conversations.items() %}
      <li class="{% if cid==conv_id %}active{% endif %}">
        <a href="?conv_id={{cid}}">{{ conv.name }}</a>
        <div>
          <button onclick="renameConversation('{{cid}}')">✏️</button>
          <button onclick="deleteConversation('{{cid}}')">🗑️</button>
        </div>
      </li>
      {% endfor %}
    </ul>
  </div>
  <div class="main">
    <div class="main-header"><h1>{{ conversations[conv_id].name }}</h1></div>
    {% if not loaded %}
    <form method="post" enctype="multipart/form-data" class="load-form">
      <input type="hidden" name="conv_id" value="{{conv_id}}">
      <input type="url" name="url" placeholder="Digite URL..." required>
      <button type="submit" name="source" value="site">Site</button>
      <button type="submit" name="source" value="pdf">PDF</button>
      <button type="submit" name="source" value="youtube">YouTube</button>
    </form>
    {% else %}
    <div class="messages" id="msgBox">
      {% for role, text in history %}
      <div class="message {{role}}">
        {% if role=='assistant' %}<strong>Kuro:</strong> {% endif %}{{text}}
      </div>
      {% endfor %}
    </div>
    <form method="post" class="input-area">
      <input type="hidden" name="conv_id" value="{{conv_id}}">
      <input type="hidden" name="loaded" value="1">
      <input type="text" name="pergunta" placeholder="Digite sua pergunta..." required autofocus>
      <button type="submit">Enviar</button>
    </form>
    {% endif %}
  </div>
  <script>
    function renameConversation(cid) { const name=prompt('Novo nome:'); if(name) window.location=`?conv_id=${cid}&rename=${encodeURIComponent(name)}`; }
    function deleteConversation(cid) { if(confirm('Excluir?')) location=`?delete=${cid}`; }
    window.onload = ()=>{const mb=document.getElementById('msgBox'); if(mb) mb.scrollTop=mb.scrollHeight;};
  </script>
</body>
</html>
'''

@app.route('/', methods=['GET','POST'])
def index():
    args = request.args
    # Nova conversa
    if 'new' in args:
        cid = str(uuid4())
        global_conversations[cid] = {'name': 'Nova conversa', 'history': [], 'context': ''}
        return redirect(url_for('index', conv_id=cid))
    # Delete
    if 'delete' in args:
        did = args.get('delete')
        global_conversations.pop(did, None)
        return redirect(url_for('index'))
    # Rename
    if 'rename' in args and 'conv_id' in args:
        cid = args.get('conv_id')
        new = args.get('rename')
        if cid in global_conversations:
            global_conversations[cid]['name'] = new
        return redirect(url_for('index', conv_id=cid))
    # Seleciona ou cria padrão
    cid = args.get('conv_id')
    if not cid or cid not in global_conversations:
        cid = str(uuid4())
        global_conversations[cid] = {'name': 'Nova conversa', 'history': [], 'context': ''}
        return redirect(url_for('index', conv_id=cid))

    conv = global_conversations[cid]
    history = conv['history']
    loaded = bool(conv['context'])

    if request.method == 'POST':
        form = request.form
        # carregar contexto
        if 'source' in form:
            src = form.get('source')
            if src == 'site':
                conv['context'] = load_site(form.get('url', ''))
            elif src == 'pdf':
                up = request.files.get('url')
                path = os.path.join('uploads', up.filename)
                os.makedirs('uploads', exist_ok=True)
                up.save(path)
                conv['context'] = load_pdf(path)
            elif src == 'youtube':
                conv['context'] = load_youtube(form.get('url', ''))
            conv['history'] = []
            loaded = True
        # processar pergunta
        elif 'pergunta' in form:
            pergunta = form.get('pergunta', '')
            history.append(('user', pergunta))
            resposta = resposta_bot(history, conv['context'])
            history.append(('assistant', resposta))
            loaded = True

    return render_template_string(
        HTML_TEMPLATE,
        conv_id=cid,
        conversations=global_conversations,
        history=history,
        loaded=loaded
    )

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
