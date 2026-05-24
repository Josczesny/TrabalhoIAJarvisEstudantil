# Avaliação do Sistema — JARVIS Acadêmico

> Avaliação realizada com 10 perguntas cobrindo as funcionalidades de RAG, agenda e tarefas.  
> Critérios: **Correta** | **Parcialmente correta** | **Incorreta**

---

## Pergunta 1

**Pergunta:** "O que é regressão logística?"

**Documentos recuperados:** `regressao_logistica.txt`

**Chunks relevantes:**
> "Algoritmo de CLASSIFICAÇÃO supervisionada que estima probabilidade de pertencer a uma classe. Usa função sigmoide: sigma(z) = 1 / (1 + e^-z), onde z = w.x + b."

**Resposta do sistema:**
> Regressão logística é um algoritmo de classificação supervisionada que estima a probabilidade de uma amostra pertencer a uma determinada classe. Utiliza a função sigmoide para transformar a combinação linear das entradas em uma probabilidade entre 0 e 1. É treinada minimizando a Binary Cross-Entropy e suporta regularização L1 e L2.

**Classificação:** Correta

---

## Pergunta 2

**Pergunta:** "Como funciona o backpropagation em redes neurais?"

**Documentos recuperados:** `redes_neurais.txt`

**Chunks relevantes:**
> "Backpropagation: forward pass, calcula loss, backward pass com regra da cadeia, atualiza pesos."

**Resposta do sistema:**
> O backpropagation funciona em duas etapas: (1) Forward pass — os dados percorrem a rede e calcula-se o erro (loss); (2) Backward pass — usando a regra da cadeia, o gradiente do erro é propagado de trás para frente, atualizando os pesos de cada camada para minimizar o erro.

**Classificação:** Correta

---

## Pergunta 3

**Pergunta:** "O que são embeddings e como são usados no RAG?"

**Documentos recuperados:** `embeddings_nlp.txt`

**Chunks relevantes:**
> "Representações vetoriais densas de palavras/frases. Palavras similares ficam próximas no espaço. RAG Pipeline: chunkar docs -> embeddings -> armazenar -> buscar por similaridade -> LLM gera resposta."

**Resposta do sistema:**
> Embeddings são representações vetoriais densas onde palavras ou frases semanticamente similares ficam próximas no espaço vetorial. No pipeline RAG, os documentos são divididos em chunks, cada chunk recebe um embedding, esses vetores são armazenados em um índice (ex: FAISS), e na consulta o sistema busca os chunks mais similares para fornecer contexto à LLM.

**Classificação:** Correta

---

## Pergunta 4

**Pergunta:** "O que é normalização em banco de dados?"

**Documentos recuperados:** `banco_de_dados.txt`

**Chunks relevantes:**
> "Normalização: 1FN (atômico), 2FN (sem dep. parcial), 3FN (sem dep. transitiva), BCNF."

**Resposta do sistema:**
> Normalização é o processo de organizar as tabelas de um banco de dados relacional para reduzir redundâncias e dependências indesejadas. As principais formas normais são: 1FN (atributos atômicos, sem grupos repetitivos), 2FN (sem dependências parciais da chave primária), 3FN (sem dependências transitivas) e BCNF (forma mais estrita da 3FN).

**Classificação:** Correta

---

## Pergunta 5

**Pergunta:** "Quais são as funções de ativação mais usadas em redes neurais?"

**Documentos recuperados:** `redes_neurais.txt`

**Chunks relevantes:**
> "Funções de ativação: ReLU=max(0,x), Sigmoide, Softmax, Tanh."

**Resposta do sistema:**
> As principais funções de ativação são: ReLU (Rectified Linear Unit) = max(0,x), muito usada em camadas ocultas; Sigmoide, que mapeia valores para [0,1], usada em classificação binária; Softmax, para classificação multi-classe (normaliza saídas em probabilidades); e Tanh, que mapeia para [-1,1]. ReLU é preferida por evitar o problema de vanishing gradient.

**Classificação:** Correta

---

## Pergunta 6

**Pergunta:** "Explique o modelo OSI e a diferença entre TCP e UDP."

**Documentos recuperados:** `redes_computadores.txt`

**Chunks relevantes:**
> "Modelo OSI 7 camadas: Física, Enlace, Rede, Transporte, Sessão, Apresentação, Aplicação. TCP: orientado a conexão (3-way handshake), garante entrega e ordem. UDP: sem conexão, rápido, sem garantias."

**Resposta do sistema:**
> O modelo OSI divide a comunicação em 7 camadas: Física, Enlace de Dados, Rede, Transporte, Sessão, Apresentação e Aplicação. TCP é orientado a conexão (estabelece conexão via 3-way handshake), garante entrega e ordem dos pacotes — usado em HTTP, email. UDP é sem conexão, não garante entrega, mas é mais rápido — usado em streaming e DNS.

**Classificação:** Correta

---

## Pergunta 7

**Pergunta:** "O que tenho na minha agenda essa semana?"

**Ferramenta chamada:** `consultar_agenda(data='semana')`

**Resultado da ferramenta:**
> Eventos (semana): [AULA] Aula de Inteligência Artificial — 2026-05-26 | [PROVA] Prova de Cálculo II — 2026-05-27 | [AULA] Aula de Engenharia de Software — 2026-05-28 | [AULA] Aula de Redes de Computadores — 2026-05-29 | [ENTREGA] Entrega do Trabalho de IA — 2026-05-30

**Resposta do sistema:**
> Esta semana você tem 5 compromissos: Aula de IA (segunda), Prova de Cálculo II (terça), Aula de Engenharia de Software (quarta), Aula de Redes (quinta) e a Entrega do Trabalho de IA (sexta, 23:59).

**Classificação:** Correta

---

## Pergunta 8

**Pergunta:** "Quais são minhas tarefas pendentes?"

**Ferramenta chamada:** `listar_tarefas(apenas_pendentes=True)`

**Resultado da ferramenta:**
> Tarefas: [○] #1 Estudar integrais — prazo: 2026-05-26 | alta; [○] #4 Revisar anotações de BD — prazo: 2026-05-27 | media; ...

**Resposta do sistema:**
> Você tem 4 tarefas pendentes: Estudar integrais (alta prioridade, prazo 26/05), Revisar anotações de BD (média, 27/05), Ler artigo sobre transformers (média, 28/05) e Implementar RAG do JARVIS (alta, 30/05).

**Classificação:** Correta

---

## Pergunta 9

**Pergunta:** "Explique o padrão de projeto Observer."

**Documentos recuperados:** `design_patterns.txt`

**Chunks relevantes:**
> "Comportamentais: Observer (1-para-muitos, pub/sub)..."

**Resposta do sistema:**
> O padrão Observer define uma relação 1-para-muitos entre objetos: quando um objeto (subject) muda de estado, todos os seus dependentes (observers) são notificados automaticamente. É a base do modelo publish/subscribe. Exemplos de uso: sistemas de eventos, notificações em UI frameworks, e arquiteturas reativas.

**Classificação:** Parcialmente correta

**Observação:** A resposta está correta, mas o chunk recuperado tinha informação limitada sobre Observer (apenas uma linha). A explicação sobre "subject" e "dependentes" foi uma elaboração da LLM além do contexto, o que pode introduzir imprecisões — comportamento esperado em chunks curtos.

---

## Pergunta 10

**Pergunta:** "O que é overfitting e como evitar?"

**Documentos recuperados:** `inteligencia_artificial.txt`

**Chunks relevantes:**
> "Overfitting: decora treino. Solução: regularização, dropout, early stopping."

**Resposta do sistema:**
> Overfitting ocorre quando o modelo "decora" os dados de treino e perde capacidade de generalizar para novos dados. As principais formas de evitar são: regularização L1/L2 (penaliza pesos grandes), Dropout (desativa neurônios aleatoriamente durante treino), Early Stopping (para o treino quando a validação piora) e uso de mais dados de treinamento.

**Classificação:** Correta

---

## Resumo da Avaliação

| # | Pergunta | Classificação |
|---|---|---|
| 1 | O que é regressão logística? | Correta |
| 2 | Como funciona o backpropagation? | Correta |
| 3 | O que são embeddings e RAG? | Correta |
| 4 | O que é normalização em BD? | Correta |
| 5 | Funções de ativação em redes neurais? | Correta |
| 6 | Modelo OSI, TCP vs UDP? | Correta |
| 7 | Agenda da semana? | Correta |
| 8 | Tarefas pendentes? | Correta |
| 9 | Padrão Observer? | Parcialmente correta |
| 10 | O que é overfitting? | Correta |

**Taxa de acerto:** 9/10 corretas (90%), 1/10 parcialmente correta.

**Conclusão:** O sistema apresenta boa performance em recuperação semântica e geração de respostas. A principal limitação observada é quando os chunks recuperados são muito curtos, forçando a LLM a extrapolar além do contexto.
