import re
import numpy as np
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer

from jarvis.config import client, MODEL, logger

CHUNK_SIZE = 400
CHUNK_OVERLAP = 60
TOP_K = 3
SCORE_MIN = 0.25  # descarta chunks com similaridade abaixo desse limiar


def chunk_texto(texto, tamanho=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Recursive chunking: tenta preservar parágrafos e frases antes de cortar por char."""
    separadores = ['\n\n', '\n', '. ', ' ']
    chunks = _split_recursivo(texto.strip(), tamanho, overlap, separadores)
    return [c for c in chunks if len(c) > 30]


def _split_recursivo(texto, tamanho, overlap, separadores):
    if len(texto) <= tamanho:
        return [texto] if texto else []
    if not separadores:
        # fallback: corte fixo
        partes, i = [], 0
        while i < len(texto):
            partes.append(texto[i:i + tamanho])
            i += tamanho - overlap
        return partes

    sep = separadores[0]
    segmentos = texto.split(sep)
    chunks, atual = [], ''
    for seg in segmentos:
        candidato = atual + (sep if atual else '') + seg
        if len(candidato) <= tamanho:
            atual = candidato
        else:
            if atual:
                chunks.append(atual)
            if len(seg) > tamanho:
                chunks.extend(_split_recursivo(seg, tamanho, overlap, separadores[1:]))
                atual = ''
            else:
                atual = seg
    if atual:
        chunks.append(atual)
    return chunks


class JARVIS_RAG:
    def __init__(self, modelo='paraphrase-multilingual-MiniLM-L12-v2'):
        self._nome_modelo = modelo
        self.modelo = None
        self.chunks, self.metadados, self.index = [], [], None

    def _get_modelo(self):
        if self.modelo is None:
            logger.info(f'Carregando modelo de embedding: {self._nome_modelo}')
            self.modelo = SentenceTransformer(self._nome_modelo)
            faiss.omp_set_num_threads(min(4, __import__('os').cpu_count() or 1))
        return self.modelo

    def carregar_documentos(self, pasta='data/documentos'):
        todos_chunks, todos_meta = [], []
        arquivos = list(Path(pasta).glob('*.txt')) + list(Path(pasta).glob('*.pdf'))
        logger.info(f'Carregando {len(arquivos)} documentos para o RAG...')
        for arq in arquivos:
            if arq.suffix == '.pdf':
                try:
                    from pypdf import PdfReader
                    texto = '\n'.join(p.extract_text() or '' for p in PdfReader(str(arq)).pages)
                except Exception as e:
                    logger.warning(f'Erro lendo PDF {arq.name}: {e}')
                    continue
            else:
                texto = arq.read_text(encoding='utf-8', errors='ignore')
            for ch in chunk_texto(texto):
                todos_chunks.append(ch)
                todos_meta.append({'arquivo': arq.name, 'pasta': pasta})

        if not todos_chunks:
            logger.warning('Nenhum chunk gerado!')
            return

        modelo = self._get_modelo()
        embeddings = modelo.encode(todos_chunks, show_progress_bar=False, batch_size=64)
        embeddings = np.array(embeddings, dtype='float32')
        faiss.normalize_L2(embeddings)

        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings)
        self.chunks = todos_chunks
        self.metadados = todos_meta
        logger.info(f'RAG: {len(self.chunks)} chunks indexados de {len(arquivos)} documentos.')

    def buscar(self, pergunta, k=TOP_K):
        if self.index is None or len(self.chunks) == 0:
            return []
        modelo = self._get_modelo()
        q_emb = modelo.encode([pergunta], show_progress_bar=False)
        q_emb = np.array(q_emb, dtype='float32')
        faiss.normalize_L2(q_emb)
        scores, idx = self.index.search(q_emb, min(k, len(self.chunks)))
        return [
            {'texto': self.chunks[i], 'arquivo': self.metadados[i]['arquivo'], 'score': float(scores[0][j])}
            for j, i in enumerate(idx[0])
            if i >= 0 and float(scores[0][j]) >= SCORE_MIN
        ]

    def responder(self, pergunta):
        chunks = self.buscar(pergunta)
        contexto = '\n\n---\n\n'.join(c['texto'] for c in chunks)
        prompt = (
            'Baseado SOMENTE no contexto abaixo, responda de forma clara e objetiva em português.\n\n'
            f'CONTEXTO:\n{contexto}\n\n'
            f'PERGUNTA: {pergunta}\n\nRESPOSTA:'
        )
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=600,
            temperature=0.3,
        )
        logger.info(f'[RAG] pergunta={pergunta[:60]} | chunks={[c["arquivo"] for c in chunks]}')
        return {'resposta': resp.choices[0].message.content, 'chunks': chunks}


rag = JARVIS_RAG()
