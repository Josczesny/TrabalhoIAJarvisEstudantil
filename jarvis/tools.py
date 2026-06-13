import datetime

from jarvis.config import client, MODEL, logger
from jarvis.data_init import carregar_json, salvar_json
from jarvis.rag import rag

QUIZ_STATE = {
    'ativo': False,
    'topico': None,
    'pergunta_atual': None,
    'contexto': None,
    'total_perguntas': 0,
}


# ── Agenda ────────────────────────────────────────────────────────────

def consultar_agenda(data=None, tipo=None):
    agenda = carregar_json('data/agenda.json')
    hoje = datetime.date.today()
    if data in ('hoje', None):
        alvo = str(hoje)
    elif data in ('amanhã', 'amanha'):
        alvo = str(hoje + datetime.timedelta(days=1))
    elif data == 'semana':
        alvo = None
    else:
        alvo = data

    if data == 'semana':
        fim = hoje + datetime.timedelta(days=7)
        evs = [e for e in agenda if hoje <= datetime.date.fromisoformat(e['data']) <= fim]
    elif alvo:
        evs = [e for e in agenda if e['data'] == alvo]
    else:
        evs = agenda

    if tipo:
        evs = [e for e in evs if e['tipo'] == tipo]

    if not evs:
        return f'Nenhum evento encontrado para {data or "hoje"}.'
    linhas = [f'Eventos ({data or "hoje"}):']
    for e in sorted(evs, key=lambda x: x['data'] + x['horario']):
        linhas.append(f"  [{e['tipo'].upper()}] {e['titulo']} — {e['data']} {e['horario']} | {e['local']}")
        if e.get('descricao'):
            linhas.append(f"    {e['descricao']}")
    return '\n'.join(linhas)


def consultar_provas_proximas(dias=7):
    agenda = carregar_json('data/agenda.json')
    hoje = datetime.date.today()
    limite = hoje + datetime.timedelta(days=dias)
    evs = [e for e in agenda
           if e['tipo'] in ('prova', 'entrega')
           and hoje <= datetime.date.fromisoformat(e['data']) <= limite]
    if not evs:
        return f'Nenhuma prova/entrega nos próximos {dias} dias.'
    linhas = [f'Provas/Entregas nos próximos {dias} dias:']
    for e in sorted(evs, key=lambda x: x['data']):
        d = (datetime.date.fromisoformat(e['data']) - hoje).days
        linhas.append(f"  {e['titulo']} — {e['data']} (em {d} dia(s)) | {e['local']}")
    return '\n'.join(linhas)


# ── Tarefas ───────────────────────────────────────────────────────────

def listar_tarefas(apenas_pendentes=True):
    tarefas = carregar_json('data/tarefas.json')
    if apenas_pendentes:
        tarefas = [t for t in tarefas if not t['concluida']]
    if not tarefas:
        return 'Nenhuma tarefa encontrada.'
    linhas = ['Tarefas:']
    for t in sorted(tarefas, key=lambda x: x['prazo']):
        status = '✓' if t['concluida'] else '○'
        linhas.append(f"  [{status}] #{t['id']} {t['titulo']} | prazo: {t['prazo']} | {t['prioridade']}")
    return '\n'.join(linhas)


def adicionar_tarefa(titulo, descricao='', prazo=None, prioridade='media'):
    tarefas = carregar_json('data/tarefas.json')
    novo_id = max((t['id'] for t in tarefas), default=0) + 1
    if not prazo:
        prazo = str(datetime.date.today() + datetime.timedelta(days=7))
    nova = {'id': novo_id, 'titulo': titulo, 'descricao': descricao,
            'prazo': prazo, 'concluida': False, 'prioridade': prioridade}
    tarefas.append(nova)
    salvar_json('data/tarefas.json', tarefas)
    return f'Tarefa #{novo_id} adicionada: "{titulo}" (prazo: {prazo}, prioridade: {prioridade})'


def concluir_tarefa(tarefa_id):
    tarefas = carregar_json('data/tarefas.json')
    try:
        tarefa_id = int(tarefa_id)
    except (TypeError, ValueError):
        return f'ID de tarefa inválido: {tarefa_id}'
    for t in tarefas:
        if t['id'] == tarefa_id:
            if t['concluida']:
                return f'Tarefa #{tarefa_id} já estava concluída.'
            t['concluida'] = True
            salvar_json('data/tarefas.json', tarefas)
            return f'✓ Tarefa #{tarefa_id} marcada como concluída: {t["titulo"]}'
    return f'Tarefa #{tarefa_id} não encontrada.'


def reabrir_tarefa(tarefa_id):
    tarefas = carregar_json('data/tarefas.json')
    try:
        tarefa_id = int(tarefa_id)
    except (TypeError, ValueError):
        return f'ID de tarefa inválido: {tarefa_id}'
    for t in tarefas:
        if t['id'] == tarefa_id:
            if not t['concluida']:
                return f'Tarefa #{tarefa_id} já está pendente.'
            t['concluida'] = False
            salvar_json('data/tarefas.json', tarefas)
            return f'Tarefa #{tarefa_id} reaberta: {t["titulo"]}'
    return f'Tarefa #{tarefa_id} não encontrada.'


# ── RAG ───────────────────────────────────────────────────────────────

def buscar_material_rag(pergunta):
    r = rag.responder(pergunta)
    nomes = sorted(set(
        c['arquivo'].replace('_', ' ').replace('.txt', '').replace('.pdf', '').title()
        for c in r['chunks']
    ))
    fontes = ', '.join(nomes)
    return f"{r['resposta']}\n\nFontes consultadas: {fontes}"


# ── Planejamento ──────────────────────────────────────────────────────

def planejar_estudos(materia=None, dias=7):
    agenda = carregar_json('data/agenda.json')
    tarefas = carregar_json('data/tarefas.json')
    hoje = datetime.date.today()
    limite = hoje + datetime.timedelta(days=dias)

    eventos = [e for e in agenda
               if e['tipo'] in ('prova', 'entrega')
               and hoje <= datetime.date.fromisoformat(e['data']) <= limite]
    tarefas_p = [t for t in tarefas if not t['concluida']]

    linhas = [f'[DADOS PARA PLANEJAMENTO — próximos {dias} dias a partir de {hoje}]']
    linhas.append('\nPROVAS/ENTREGAS PRÓXIMAS:')
    if eventos:
        for e in sorted(eventos, key=lambda x: x['data']):
            d = (datetime.date.fromisoformat(e['data']) - hoje).days
            linhas.append(f"  • {e['titulo']} — {e['data']} (em {d} dia(s)) | {e['descricao']}")
    else:
        linhas.append('  Nenhuma prova/entrega nos próximos dias.')

    linhas.append('\nTAREFAS PENDENTES (por prioridade):')
    if tarefas_p:
        ordem = {'alta': 0, 'media': 1, 'baixa': 2}
        for t in sorted(tarefas_p, key=lambda x: (ordem.get(x['prioridade'], 1), x['prazo'])):
            linhas.append(f"  • [{t['prioridade'].upper()}] {t['titulo']} — prazo: {t['prazo']}")
    else:
        linhas.append('  Nenhuma tarefa pendente.')

    if materia:
        chunks = rag.buscar(materia, k=4)
        if chunks:
            nome_mat = materia.title()
            linhas.append(f'\nCONTEÚDO DISPONÍVEL SOBRE "{nome_mat}":')
            for c in chunks[:2]:
                linhas.append(f"  {c['texto'][:180]}...")

    logger.info(f'[PLANEJAR] materia={materia} dias={dias}')
    return '\n'.join(linhas)


# ── Aprendizado ───────────────────────────────────────────────────────

def gerar_exercicios(topico, quantidade=3):
    chunks = rag.buscar(topico, k=4)
    if not chunks:
        return f"Não encontrei material sobre '{topico}'. Tente: regressão logística, redes neurais, banco de dados, etc."
    contexto = '\n\n'.join(c['texto'] for c in chunks)
    prompt = (
        f"Com base no conteúdo abaixo, crie exatamente {quantidade} exercícios de revisão sobre '{topico}'. "
        f"Misture questões abertas e de múltipla escolha. Numere cada exercício.\n"
        f"Ao final, inclua 'GABARITO:' com as respostas corretas.\n\nCONTEÚDO:\n{contexto}"
    )
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=700,
        temperature=0.6,
    )
    nomes = sorted(set(
        c['arquivo'].replace('_', ' ').replace('.txt', '').replace('.pdf', '').title()
        for c in chunks
    ))
    logger.info(f'[EXERCICIOS] topico={topico} quantidade={quantidade} | fontes={nomes}')
    return f"{resp.choices[0].message.content}\n\nFontes consultadas: {', '.join(nomes)}"


def iniciar_quiz(topico):
    chunks = rag.buscar(topico, k=3)
    if not chunks:
        return f"Não encontrei material sobre '{topico}' para criar um quiz."
    contexto = '\n\n'.join(c['texto'] for c in chunks)
    prompt = (
        f"Com base no conteúdo abaixo sobre '{topico}', crie UMA pergunta de revisão clara e objetiva. "
        f"Apenas a pergunta, sem dar a resposta.\n\nCONTEÚDO:\n{contexto}"
    )
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=120,
        temperature=0.7,
    )
    pergunta = resp.choices[0].message.content.strip()
    QUIZ_STATE.update({
        'ativo': True, 'topico': topico,
        'pergunta_atual': pergunta, 'contexto': contexto,
        'total_perguntas': QUIZ_STATE['total_perguntas'] + 1,
    })
    logger.info(f'[QUIZ] Iniciado: topico={topico}')
    return f"Quiz iniciado sobre **{topico}**!\n\n**Pergunta:** {pergunta}\n\n*(Responda no chat e eu avaliarei sua resposta!)*"


def verificar_resposta_quiz(resposta_usuario):
    if not QUIZ_STATE['ativo'] or not QUIZ_STATE['pergunta_atual']:
        return "Não há quiz ativo no momento. Diga 'iniciar quiz sobre [tópico]' para começar."
    prompt = (
        f"Você é um professor avaliando a resposta de um aluno. Seja encorajador. Nunca comece com saudações como 'Olá', 'Oi' ou similares — vá direto à avaliação.\n\n"
        f"PERGUNTA: {QUIZ_STATE['pergunta_atual']}\n"
        f"RESPOSTA DO ALUNO: {resposta_usuario}\n\n"
        f"CONTEÚDO DE REFERÊNCIA:\n{QUIZ_STATE['contexto']}\n\n"
        f"1. Classifique: Correta / Parcialmente correta / Incorreta\n"
        f"2. Explique o que estava certo e o que faltou\n"
        f"3. Dê o gabarito completo\n"
        f"4. Faça UMA nova pergunta diferente sobre o mesmo tema para continuar"
    )
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=500,
        temperature=0.4,
    )
    resultado = resp.choices[0].message.content
    novas = [l.strip() for l in resultado.split('\n') if l.strip() and '?' in l]
    if novas:
        QUIZ_STATE['pergunta_atual'] = novas[-1]
        QUIZ_STATE['total_perguntas'] += 1
    logger.info(f'[QUIZ] Avaliação: topico={QUIZ_STATE["topico"]} resposta={resposta_usuario[:50]}')
    return resultado


