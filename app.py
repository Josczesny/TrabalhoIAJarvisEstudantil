# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
import logging

from jarvis.data_init import inicializar, carregar_json
from jarvis.rag import rag
from jarvis.tools import adicionar_tarefa, concluir_tarefa, QUIZ_STATE
from jarvis.agent import jarvis, HISTORICO

logger = logging.getLogger('JARVIS')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

inicializar()
rag.carregar_documentos()

# ── Rotas ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('mensagem', '').strip()
    if not msg:
        return jsonify({'erro': 'Mensagem vazia'}), 400
    try:
        resposta = jarvis(msg)
        return jsonify({'resposta': resposta})
    except Exception as e:
        logger.error(f'Erro no chat: {e}')
        return jsonify({'erro': str(e)}), 500


@app.route('/limpar', methods=['POST'])
def limpar():
    HISTORICO.clear()
    return jsonify({'ok': True})


@app.route('/agenda')
def agenda():
    return jsonify(carregar_json('data/agenda.json'))


@app.route('/tarefas')
def tarefas():
    return jsonify(carregar_json('data/tarefas.json'))


@app.route('/documentos')
def listar_documentos():
    pasta = Path('data/documentos')
    arquivos = [f.name for f in sorted(pasta.glob('*')) if f.suffix in ('.txt', '.pdf')]
    return jsonify(arquivos)


@app.route('/concluir_tarefa', methods=['POST'])
def rota_concluir():
    data = request.json
    resultado = concluir_tarefa(data.get('id'))
    return jsonify({'ok': True, 'resultado': resultado})


@app.route('/adicionar_tarefa', methods=['POST'])
def rota_adicionar():
    data = request.json
    resultado = adicionar_tarefa(
        titulo=data.get('titulo', ''),
        descricao=data.get('descricao', ''),
        prazo=data.get('prazo'),
        prioridade=data.get('prioridade', 'media'),
    )
    return jsonify({'ok': True, 'resultado': resultado})


@app.route('/quiz_estado')
def quiz_estado():
    return jsonify({
        'ativo': QUIZ_STATE['ativo'],
        'topico': QUIZ_STATE['topico'],
        'total_perguntas': QUIZ_STATE['total_perguntas'],
    })


@app.route('/upload', methods=['POST'])
def upload():
    if 'arquivo' not in request.files:
        return jsonify({'erro': 'Nenhum arquivo enviado'}), 400
    arq = request.files['arquivo']
    if arq.filename == '':
        return jsonify({'erro': 'Nome de arquivo vazio'}), 400
    nome = secure_filename(arq.filename)
    destino = Path('data/documentos') / nome
    arq.save(destino)
    logger.info(f'Arquivo enviado: {nome}')
    rag.carregar_documentos()
    return jsonify({'ok': True, 'arquivo': nome})


if __name__ == '__main__':
    print('\n' + '=' * 55)
    print('JARVIS Acadêmico — rodando em http://localhost:5000')
    print('=' * 55 + '\n')
    app.run(debug=False, port=5000, threaded=True)
