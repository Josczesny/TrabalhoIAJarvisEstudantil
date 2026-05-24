# Análise de Erros — JARVIS Acadêmico

Identificação de falhas observadas durante testes do sistema.

---

## Falha 1 — Chunks muito curtos causam extrapolação da LLM

**Tipo:** Geração (alucinação por contexto insuficiente)

**Causa:**
O chunking por caracteres (tamanho fixo de 200 chars com overlap de 30) pode gerar chunks que capturam apenas parte de uma explicação. Quando o chunk recuperado é muito curto ou incompleto, a LLM complementa a resposta com conhecimento próprio — saindo do contexto fornecido e potencialmente introduzindo informações não presentes nos documentos.

**Exemplo observado:**
Na Pergunta 9 (padrão Observer), o chunk recuperado tinha apenas: `"Comportamentais: Observer (1-para-muitos, pub/sub)"`. A LLM adicionou detalhes sobre "subject", "observers" e "UI frameworks" que não constavam no documento.

**Possível solução:**
- Aumentar `CHUNK_SIZE` para 400-500 chars, preservando mais contexto por chunk
- Usar chunking semântico (por parágrafo ou seção) em vez de tamanho fixo
- Adicionar verificação de score mínimo de similaridade antes de usar o chunk

---

## Falha 2 — Dependência de data hardcoded na agenda

**Tipo:** Ambiguidade temporal / recuperação desatualizada

**Causa:**
Os eventos da agenda (`data/agenda.json`) tinham datas fixas em maio/junho de 2025. Quando o sistema era executado em outra data (ex: 2026), consultas como "O que tenho hoje?" retornavam "Nenhum evento encontrado" pois nenhum evento correspondia à data real.

**Exemplo observado:**
Ao rodar em 2026-05-23, `consultar_agenda(data='hoje')` retornava resposta vazia porque todos os eventos eram de 2025.

**Solução implementada:**
As datas em `AGENDA_INICIAL` e nos arquivos `data/agenda.json` e `data/tarefas.json` foram atualizadas para maio/junho de 2026. A longo prazo, a correção ideal é gerar datas relativas usando `datetime.date.today() + timedelta(...)` na inicialização.

**Status:** Resolvido (datas atualizadas para 2026)

---

## Falha 3 — Tool calling falha em perguntas ambíguas

**Tipo:** Seleção de ferramenta / ambiguidade semântica

**Causa:**
Quando o usuário faz uma pergunta que mistura duas intenções (ex: "O que tenho para estudar hoje?"), a LLM pode chamar apenas `consultar_agenda` (interpretando como agenda) em vez de combinar `consultar_agenda` + `listar_tarefas` + `consultar_provas_proximas`. O modelo Gemma 12B às vezes seleciona apenas uma ferramenta quando múltiplas seriam necessárias.

**Exemplo observado:**
"O que devo estudar hoje?" → LLM chama apenas `buscar_material_rag` com pergunta genérica, ignorando que o usuário provavelmente quer saber sobre provas próximas e tarefas pendentes também.

**Possível solução:**
- Enriquecer as descrições das ferramentas com mais exemplos de quando usá-las em conjunto
- Adicionar no system prompt exemplos explícitos de chamadas múltiplas: "Para 'o que estudar hoje', combine consultar_agenda + listar_tarefas + consultar_provas_proximas"
- Implementar um agente de roteamento dedicado que analisa a intenção antes de chamar ferramentas

---

## Resumo

| # | Tipo | Impacto | Complexidade da Solução |
|---|---|---|---|
| 1 | Geração — alucinação por chunk curto | Médio | Média (ajustar chunking) |
| 2 | Recuperação — datas desatualizadas | Alto | Baixa (datas dinâmicas) |
| 3 | Tool calling — ambiguidade de intenção | Médio | Alta (melhorar prompts/roteamento) |
