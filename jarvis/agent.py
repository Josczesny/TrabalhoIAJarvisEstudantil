import json
import re

from jarvis.config import client, MODEL, logger
from jarvis.tools import (
    consultar_agenda, listar_tarefas, adicionar_tarefa, concluir_tarefa,
    buscar_material_rag, consultar_provas_proximas, planejar_estudos,
    gerar_exercicios, iniciar_quiz, verificar_resposta_quiz, QUIZ_STATE,
)

HISTORICO = []

# Ferramentas que já geram resposta final via LLM interno — retornar sem segundo LLM
DIRETO = {'iniciar_quiz', 'verificar_resposta_quiz', 'gerar_exercicios'}

FERRAMENTAS_EXEC = {
    'consultar_agenda':          lambda a: consultar_agenda(**a),
    'listar_tarefas':            lambda a: listar_tarefas(**a),
    'adicionar_tarefa':          lambda a: adicionar_tarefa(**a),
    'concluir_tarefa':           lambda a: concluir_tarefa(**a),
    'buscar_material_rag':       lambda a: buscar_material_rag(**a),
    'consultar_provas_proximas': lambda a: consultar_provas_proximas(**a),
    'planejar_estudos':          lambda a: planejar_estudos(**a),
    'gerar_exercicios':          lambda a: gerar_exercicios(**a),
    'iniciar_quiz':              lambda a: iniciar_quiz(**a),
    'verificar_resposta_quiz':   lambda a: verificar_resposta_quiz(**a),
}

SYSTEM_PROMPT = (
    'Você é o JARVIS, assistente acadêmico inteligente e amigável.\n'
    'Você ajuda estudantes com materiais de estudo, agenda, tarefas, planejamento e aprendizado ativo.\n'
    'Quando receber dados do sistema antes da pergunta do usuário, use-os para responder com precisão.\n'
    'IMPORTANTE: NUNCA se apresente ou cumprimente no início da resposta. Vá direto ao ponto.\n'
    'Não diga "Olá", "Oi", "Sou o JARVIS" ou qualquer saudação. Responda diretamente ao que foi pedido.\n'
    'Seja objetivo, claro e encorajador. Use markdown para formatar a resposta.\n'
    'Responda sempre em português brasileiro.\n'
    'Nunca use emojis ou símbolos decorativos na resposta.\n'
    'Não liste ou cite os nomes de arquivos/fontes na sua resposta. Essa informação é gerenciada pelo sistema.'
)

# Prompt que pede à LLM para selecionar as ferramentas em JSON
TOOL_SELECTOR_PROMPT = """\
Você é um agente que seleciona ferramentas para responder ao usuário.

Ferramentas disponíveis:
- consultar_agenda(data): agenda. data = "hoje", "amanha", "semana" ou YYYY-MM-DD
- listar_tarefas(): lista tarefas pendentes
- adicionar_tarefa(titulo, prazo, prioridade): cria tarefa. prioridade: alta/media/baixa
- concluir_tarefa(tarefa_id): conclui tarefa (id numérico)
- buscar_material_rag(pergunta): busca em materiais de estudo sobre qualquer conteúdo academico
- consultar_provas_proximas(dias): provas e entregas proximas (padrao 7 dias)
- planejar_estudos(materia, dias): monta plano de estudos combinando agenda + tarefas
- gerar_exercicios(topico, quantidade): gera exercicios com gabarito (padrao 3)
- iniciar_quiz(topico): inicia quiz de active recall
- verificar_resposta_quiz(resposta_usuario): avalia resposta do quiz ativo

Estado atual:
- quiz_ativo: {quiz_ativo}
- topico_quiz: {quiz_topico}

Regras:
1. Se quiz_ativo=true e o usuario nao pediu explicitamente outra acao, use verificar_resposta_quiz
2. Para conteudo academico (explicar, o que e, como funciona), use buscar_material_rag
3. Combine ferramentas quando necessario (veja exemplos abaixo)
4. Use apenas ferramentas relevantes para a mensagem

Exemplos (few-shot):
Mensagem: "o que devo estudar hoje?"
{{"ferramentas": [{{"nome": "consultar_agenda", "args": {{"data": "hoje"}}}}, {{"nome": "listar_tarefas", "args": {{}}}}, {{"nome": "consultar_provas_proximas", "args": {{"dias": 7}}}}]}}

Mensagem: "monte um plano de estudos para a prova de redes"
{{"ferramentas": [{{"nome": "planejar_estudos", "args": {{"materia": "redes de computadores", "dias": 7}}}}]}}

Mensagem: "adiciona tarefa de estudar grafos para sexta"
{{"ferramentas": [{{"nome": "adicionar_tarefa", "args": {{"titulo": "Estudar grafos", "prioridade": "media"}}}}]}}

Mensagem: "explique backpropagation"
{{"ferramentas": [{{"nome": "buscar_material_rag", "args": {{"pergunta": "como funciona backpropagation em redes neurais"}}}}]}}

Mensagem: "quais são minhas provas essa semana?"
{{"ferramentas": [{{"nome": "consultar_provas_proximas", "args": {{"dias": 7}}}}, {{"nome": "consultar_agenda", "args": {{"data": "semana"}}}}]}}

Responda SOMENTE com JSON valido, sem texto adicional:
{{"ferramentas": [{{"nome": "nome_da_ferramenta", "args": {{"param": "valor"}}}}]}}

Mensagem: {mensagem}"""


def _selecionar_com_llm(msg: str) -> list:
    """LLM seleciona ferramentas. Retorna [{nome, args}, ...]."""
    prompt = TOOL_SELECTOR_PROMPT.format(
        quiz_ativo=str(QUIZ_STATE['ativo']).lower(),
        quiz_topico=QUIZ_STATE['topico'] or 'nenhum',
        mensagem=msg,
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=300,
            temperature=0.1,
        )
        content = resp.choices[0].message.content.strip()
        # Extrai JSON mesmo que a LLM adicione texto extra
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            data = json.loads(match.group())
            ferramentas = data.get('ferramentas', [])
            if isinstance(ferramentas, list):
                valid = [
                    f for f in ferramentas
                    if isinstance(f.get('nome'), str) and isinstance(f.get('args', {}), dict)
                ]
                if valid:
                    logger.info(f'[LLM SELECT] ferramentas={[f["nome"] for f in valid]}')
                    return valid
    except Exception as e:
        logger.warning(f'[LLM SELECT FAIL] {e} — usando fallback por palavras-chave')

    return _fallback_keywords(msg)


def _fallback_keywords(msg: str) -> list:
    """Fallback por palavras-chave quando a seleção via LLM falha."""
    m = msg.lower()

    SAIDA_QUIZ = ('gere ', 'crie ', 'monte ', 'explique ', 'listar', 'agenda', 'tarefas',
                  'parar quiz', 'encerrar quiz', 'sair do quiz', 'cancelar quiz', 'quiz sobre')
    sair_quiz = any(m.startswith(p) or p in m for p in SAIDA_QUIZ)

    if QUIZ_STATE['ativo'] and sair_quiz:
        QUIZ_STATE['ativo'] = False
        logger.info('[QUIZ] Encerrado por comando — fallback')
    elif QUIZ_STATE['ativo']:
        return [{'nome': 'verificar_resposta_quiz', 'args': {'resposta_usuario': msg}}]

    if any(w in m for w in ('quiz', 'active recall', 'me teste', 'questionar', 'teste de conhecimento')):
        match = re.search(r'\bsobre\s+(.+)', m)
        topico = match.group(1).strip() if match else 'geral'
        return [{'nome': 'iniciar_quiz', 'args': {'topico': topico}}]

    if any(w in m for w in ('exercício', 'exercicios', 'gere', 'crie exerc', 'questão', 'questoes', 'praticar')):
        match = re.search(r'\bsobre\s+(.+)', m)
        topico = match.group(1).strip() if match else m
        return [{'nome': 'gerar_exercicios', 'args': {'topico': topico}}]

    resultado = []

    if any(w in m for w in ('plano', 'planejamento', 'priorizar', 'organizar estudos', 'como estudar')):
        resultado.append({'nome': 'planejar_estudos', 'args': {}})

    if any(w in m for w in ('prova', 'provas', 'entrega', 'avaliação')):
        resultado.append({'nome': 'consultar_provas_proximas', 'args': {}})

    if any(w in m for w in ('agenda', 'aula', 'evento', 'horário', 'calendário', 'quando', 'hoje', 'amanhã', 'semana')):
        resultado.append({'nome': 'consultar_agenda', 'args': {'data': 'semana'}})

    if any(w in m for w in ('tarefa', 'tarefas', 'pendente', 'pendentes', 'afazeres', 'o que tenho')):
        resultado.append({'nome': 'listar_tarefas', 'args': {}})

    temas = ('redes', 'banco', 'cálculo', 'calculo', 'estrutura', 'algoritmo', 'inteligência', 'inteligencia',
             'engenharia', 'design', 'padrão', 'padroes', 'embedding', 'nlp', 'regressão', 'regressao',
             'grafo', 'árvore', 'arvore', 'hash', 'normaliz', 'acid', 'sql', 'tcp', 'osi', 'http',
             'integral', 'derivad', 'transformer', 'backprop', 'neural', 'overfitting', 'softmax')
    if any(t in m for t in temas) or any(w in m for w in ('explique', 'o que é', 'como funciona', 'o que são')):
        resultado.append({'nome': 'buscar_material_rag', 'args': {'pergunta': msg}})

    if not resultado:
        resultado.append({'nome': 'buscar_material_rag', 'args': {'pergunta': msg}})

    return resultado


def _historico_valido(hist: list) -> list:
    """Garante alternância user/assistant."""
    if not hist:
        return hist
    limpo = [hist[0]]
    for msg in hist[1:]:
        if msg['role'] != limpo[-1]['role']:
            limpo.append(msg)
        else:
            limpo[-1] = msg
    return limpo


def jarvis(msg_usuario: str) -> str:
    # Evita mensagens user consecutivas no histórico
    while HISTORICO and HISTORICO[-1]['role'] == 'user':
        HISTORICO.pop()
    HISTORICO.append({'role': 'user', 'content': msg_usuario})

    # Passo 1: LLM decide quais ferramentas chamar
    chamadas = _selecionar_com_llm(msg_usuario)

    # Passo 2: Executa as ferramentas
    resultados_ctx = {}
    direto_resultado = None

    for chamada in chamadas:
        nome = chamada.get('nome', '')
        args = chamada.get('args', {}) or {}

        if nome not in FERRAMENTAS_EXEC:
            logger.warning(f'[TOOL] Ferramenta desconhecida ignorada: {nome}')
            continue

        try:
            resultado = FERRAMENTAS_EXEC[nome](args)
            logger.info(f'[TOOL] {nome}(args={args}) -> {str(resultado)[:100]}')
        except Exception as e:
            logger.error(f'[TOOL ERROR] {nome}(args={args}): {e}')
            resultado = f'Erro ao executar {nome}: {e}'

        if nome in DIRETO:
            direto_resultado = resultado
            break
        else:
            resultados_ctx[nome] = resultado

    # Passo 3: Ferramentas diretas retornam sem segundo LLM
    if direto_resultado is not None:
        HISTORICO.append({'role': 'assistant', 'content': direto_resultado})
        return direto_resultado

    # Passo 4: LLM sintetiza resposta usando o contexto coletado
    contexto = '\n\n'.join(f'[{nome}]\n{r}' for nome, r in resultados_ctx.items())
    hist_recente = _historico_valido(HISTORICO[-20:])
    mensagens = [{'role': 'system', 'content': SYSTEM_PROMPT}]

    if contexto and hist_recente and hist_recente[-1]['role'] == 'user':
        mensagens += hist_recente[:-1]
        mensagens.append({'role': 'user', 'content': f'Informações do sistema:\n\n{contexto}'})
        mensagens.append({'role': 'assistant', 'content': 'Certo, vou usar essas informações.'})
        mensagens.append(hist_recente[-1])
    else:
        mensagens += hist_recente

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=mensagens,
            max_tokens=800,
            temperature=0.4,
        )
        texto = resp.choices[0].message.content or 'Não consegui gerar uma resposta.'
    except Exception as e:
        logger.error(f'Erro LLM: {e}')
        texto = f'Erro ao conectar ao modelo: {e}'

    HISTORICO.append({'role': 'assistant', 'content': texto})
    return texto
