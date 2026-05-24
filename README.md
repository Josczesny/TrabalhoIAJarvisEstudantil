# JARVIS Acadêmico

Assistente pessoal acadêmico com RAG, Tool Calling, Planejamento e Aprendizado Ativo — LLM Gemma 12B.

## Instalação rápida

```bash
# 1. Crie e ative um ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute
python app.py
```

Acesse: `http://localhost:5000`

## Estrutura do projeto

```text
projeto/
├── app.py                  ← backend Flask (entrada principal)
├── jarvis/
│   ├── __init__.py
│   ├── config.py           ← cliente LLM e logger
│   ├── data_init.py        ← dados iniciais e helpers JSON
│   ├── rag.py              ← RAG: chunking, embeddings, FAISS
│   ├── tools.py            ← 10 ferramentas do agente
│   └── agent.py            ← loop do agente e tool calling
├── requirements.txt
├── avaliacao.md            ← avaliação com 10 perguntas
├── analise_erros.md        ← análise de 3 falhas identificadas
├── templates/
│   └── index.html          ← interface gráfica
└── data/
    ├── agenda.json         ← criado automaticamente
    ├── tarefas.json        ← criado automaticamente
    └── documentos/         ← 10 TXTs acadêmicos + uploads do usuário
```

## Funcionalidades

### Trabalho 1

| Funcionalidade | Descrição |
| --- | --- |
| RAG (3.1) | Busca semântica com MiniLM + FAISS, chunking e geração com Gemma 12B |
| Agenda (3.2) | Consulta hoje/amanhã/semana, filtra por tipo (aula/prova/entrega) |
| Tarefas (3.3) | Adicionar, listar e concluir tarefas via chat ou interface |
| Tool Calling | 10 ferramentas com decisão feita pela LLM, logs em `jarvis_logs.log` |
| Interface gráfica | UI dark sci-fi com sidebar de agenda, tarefas e aprendizado |

### Trabalho 2

| Funcionalidade | Descrição |
| --- | --- |
| Planejamento (3.4) | `planejar_estudos` combina agenda + tarefas + RAG em um plano |
| Active Recall | `iniciar_quiz` + `verificar_resposta_quiz` — quiz interativo com avaliação |
| Exercícios | `gerar_exercicios` — questões com gabarito sobre qualquer tópico |
| Avaliação | 10 perguntas testadas — ver `avaliacao.md` |
| Análise de erros | 3 falhas identificadas — ver `analise_erros.md` |

## Ferramentas (Tool Calling)

| Ferramenta | Descrição |
| --- | --- |
| `consultar_agenda` | Eventos por data e tipo |
| `listar_tarefas` | Tarefas pendentes ou todas |
| `adicionar_tarefa` | Cria nova tarefa |
| `concluir_tarefa` | Marca tarefa como feita |
| `buscar_material_rag` | Busca semântica nos documentos |
| `consultar_provas_proximas` | Provas/entregas nos próximos N dias |
| `planejar_estudos` | Plano combinando agenda + tarefas + material |
| `gerar_exercicios` | Questões de prática com gabarito |
| `iniciar_quiz` | Inicia quiz de active recall |
| `verificar_resposta_quiz` | Avalia resposta e continua o quiz |

## Ferramentas de desenvolvimento

- **Gemma 12B** (Google via API do professor) — LLM do sistema

## Dataset

10 documentos em `data/documentos/`:

| Arquivo | Conteúdo |
| --- | --- |
| `regressao_logistica.txt` | Sigmoide, cross-entropy, regularização |
| `redes_neurais.txt` | Neurônios, backpropagation, dropout |
| `embeddings_nlp.txt` | Word2Vec, Sentence Transformers, RAG pipeline |
| `banco_de_dados.txt` | SQL, normalização, ACID, índices |
| `estrutura_de_dados.txt` | BST, grafos, BFS/DFS, Dijkstra |
| `calculo_integrais.txt` | Integrais, substituição, partes |
| `redes_computadores.txt` | OSI, TCP/UDP, IPv4/IPv6, roteamento |
| `design_patterns.txt` | GoF, SOLID, Observer, Strategy |
| `inteligencia_artificial.txt` | ML supervisionado, overfitting, métricas |
| `engenharia_software.txt` | SDLC, Scrum, Git, qualidade |

**Chunking**: tamanho 200 chars, overlap 30 chars.

**Embeddings**: `paraphrase-MiniLM-L3-v2` (~60MB, rápido para 16GB RAM).

**Index**: FAISS `IndexFlatIP` com normalização L2 (similaridade coseno).
