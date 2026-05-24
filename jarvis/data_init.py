import json
from pathlib import Path

AGENDA_INICIAL = [
    {'id': 1, 'titulo': 'Aula de Inteligência Artificial', 'tipo': 'aula', 'data': '2026-05-26', 'horario': '08:00', 'local': 'Sala 101', 'descricao': 'Tema: Redes Neurais'},
    {'id': 2, 'titulo': 'Aula de Banco de Dados', 'tipo': 'aula', 'data': '2026-05-26', 'horario': '10:00', 'local': 'Sala 203', 'descricao': 'Tema: Transações'},
    {'id': 3, 'titulo': 'Prova de Cálculo II', 'tipo': 'prova', 'data': '2026-05-27', 'horario': '14:00', 'local': 'Sala 305', 'descricao': 'Conteúdo: Integrais'},
    {'id': 4, 'titulo': 'Aula de Engenharia de Software', 'tipo': 'aula', 'data': '2026-05-28', 'horario': '08:00', 'local': 'Lab 2', 'descricao': 'Tema: Design Patterns'},
    {'id': 5, 'titulo': 'Entrega do Trabalho de IA', 'tipo': 'entrega', 'data': '2026-05-30', 'horario': '23:59', 'local': 'Online', 'descricao': 'JARVIS — Trabalho 2'},
    {'id': 6, 'titulo': 'Aula de Redes de Computadores', 'tipo': 'aula', 'data': '2026-05-29', 'horario': '10:00', 'local': 'Sala 110', 'descricao': 'Tema: TCP/IP'},
    {'id': 7, 'titulo': 'Prova de Estrutura de Dados', 'tipo': 'prova', 'data': '2026-06-02', 'horario': '08:00', 'local': 'Sala 101', 'descricao': 'Conteúdo: Árvores e Grafos'},
]

TAREFAS_INICIAL = [
    {'id': 1, 'titulo': 'Estudar integrais para a prova', 'descricao': 'Caps 5 e 6', 'prazo': '2026-05-26', 'concluida': False, 'prioridade': 'alta'},
    {'id': 2, 'titulo': 'Ler artigo sobre transformers', 'descricao': 'Attention is All You Need', 'prazo': '2026-05-28', 'concluida': False, 'prioridade': 'media'},
    {'id': 3, 'titulo': 'Implementar RAG do JARVIS', 'descricao': 'Trabalho prático', 'prazo': '2026-05-30', 'concluida': False, 'prioridade': 'alta'},
    {'id': 4, 'titulo': 'Revisar anotações de BD', 'descricao': 'Foco em normalização', 'prazo': '2026-05-27', 'concluida': False, 'prioridade': 'media'},
]

DOCS = {
    'regressao_logistica.txt': '''# Regressão Logística
Algoritmo de CLASSIFICAÇÃO supervisionada que estima probabilidade de pertencer a uma classe.
Usa função sigmoide: sigma(z) = 1 / (1 + e^-z), onde z = w.x + b.
Treinado minimizando Binary Cross-Entropy: L = -[y*log(y_hat) + (1-y)*log(1-y_hat)].
Regularização L1 (esparsidade) e L2 (penaliza pesos grandes).
Usar quando: classificação binária, dados linearmente separáveis, precisa de probabilidade.''',

    'redes_neurais.txt': '''# Redes Neurais Artificiais
Neurônio artificial: recebe entradas xi, multiplica por pesos, soma bias, passa por ativação.
Funções de ativação: ReLU=max(0,x), Sigmoide, Softmax, Tanh.
Arquitetura: entrada -> camadas ocultas -> saída.
Backpropagation: forward pass, calcula loss, backward pass com regra da cadeia, atualiza pesos.
Regularização: Dropout (desativa neurônios aleatoriamente), Batch Norm, Early Stopping.''',

    'embeddings_nlp.txt': '''# Embeddings em NLP
Representações vetoriais densas de palavras/frases. Palavras similares ficam próximas no espaço.
Word2Vec: Skip-gram (prediz vizinhos) ou CBOW (prediz palavra central).
Sentence Transformers: baseados em BERT, geram embeddings para sentenças.
Similaridade Coseno: cos(theta) = (A.B)/(|A||B|), varia de -1 a 1.
RAG Pipeline: chunkar docs -> embeddings -> armazenar -> buscar por similaridade -> LLM gera resposta.''',

    'banco_de_dados.txt': '''# Banco de Dados Relacionais
Modelo relacional: tabelas com linhas (tuplas) e colunas (atributos). Criado por Codd (1970).
SQL: SELECT, INSERT, UPDATE, DELETE, JOIN.
Chaves: Primária (PK) = identificador único; Estrangeira (FK) = referencia PK de outra tabela.
Normalização: 1FN (atômico), 2FN (sem dep. parcial), 3FN (sem dep. transitiva), BCNF.
ACID: Atomicidade, Consistência, Isolamento, Durabilidade. Índices: B-Tree, Hash.''',

    'estrutura_de_dados.txt': '''# Estruturas de Dados
BST: filho esq < pai < filho dir. Busca O(h).
Árvores balanceadas: AVL (rotações mantém |h_esq - h_dir| <= 1), Red-Black.
Grafos: vértices V + arestas E. Dirigido, não-dirigido, ponderado.
BFS (fila, menor caminho), DFS (pilha/recursão, detecta ciclos).
Dijkstra: menor caminho pesos positivos. Kruskal/Prim: MST.
Hash: O(1) médio. Complexidades: O(1) array, O(log n) busca binária, O(n log n) merge sort.''',

    'calculo_integrais.txt': '''# Cálculo II — Integrais
Integral definida: area sob a curva. Teorema Fundamental: integral(a,b) f(x)dx = F(b)-F(a).
Substituição (u-sub): u=g(x), du=g(x)dx. Exemplo: integral 2x*cos(x^2)dx = sen(x^2)+C.
Integração por Partes: integral u dv = uv - integral v du. Regra LIATE.
Frações Parciais: decompõe racionais em frações simples.
Integrais impróprias: intervalo infinito ou descontinuidade. Aplicações: área, volume, arco.''',

    'redes_computadores.txt': '''# Redes de Computadores
Modelo OSI 7 camadas: Física, Enlace, Rede, Transporte, Sessão, Apresentação, Aplicação.
TCP: orientado a conexão (3-way handshake), garante entrega e ordem, controle de fluxo.
UDP: sem conexão, rápido, sem garantias. Uso: DNS, streaming, jogos.
IPv4: 32 bits. IPv6: 128 bits. CIDR: ex 192.168.1.0/24 = 256 endereços.
HTTP (80/443), DNS (53), DHCP, SSH (22). Roteamento: RIP, OSPF (Dijkstra), BGP.''',

    'design_patterns.txt': '''# Design Patterns (GoF)
Criacionais: Singleton (única instância), Factory Method, Builder.
Estruturais: Adapter (converte interface), Decorator (adiciona responsabilidades), Facade.
Comportamentais: Observer (1-para-muitos, pub/sub), Strategy (algoritmos intercambiáveis), Command (undo/redo).
SOLID: Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion.''',

    'inteligencia_artificial.txt': '''# Inteligência Artificial
Aprendizado Supervisionado: pares (entrada, saída). Algoritmos: regressão, SVM, árvores, redes neurais.
Não Supervisionado: sem rótulos. K-Means, PCA.
Por Reforço: agente maximiza recompensa por tentativa e erro.
Overfitting: decora treino. Solução: regularização, dropout, early stopping.
Métricas: acurácia, precisão, recall, F1, ROC-AUC, MSE, MAE, R2.
Transformers: atenção (Self-Attention). BERT bidirecional, GPT autoregressivo. RAG = LLM + busca.''',

    'engenharia_software.txt': '''# Engenharia de Software
SDLC: Requisitos, Análise, Implementação, Testes, Implantação, Manutenção.
Waterfall: sequencial, requisitos estáveis. Scrum: sprints 1-4 sem, PO/SM/Dev, backlog.
Kanban: fluxo contínuo, limita WIP. Testes: unitário, integração, sistema, aceitação, regressão.
Git: commit, branch, merge, pull request, rebase.
Qualidade: SOLID, DRY, KISS. Code Review, Refatoração, Débito Técnico.''',
}


def salvar_json(caminho, dados):
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_json(caminho, padrao=None):
    try:
        with open(caminho, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return padrao if padrao is not None else []


def inicializar():
    Path('data/documentos').mkdir(parents=True, exist_ok=True)
    if not Path('data/agenda.json').exists():
        salvar_json('data/agenda.json', AGENDA_INICIAL)
    if not Path('data/tarefas.json').exists():
        salvar_json('data/tarefas.json', TAREFAS_INICIAL)
    for nome, conteudo in DOCS.items():
        p = Path(f'data/documentos/{nome}')
        if not p.exists():
            p.write_text(conteudo.strip(), encoding='utf-8')
