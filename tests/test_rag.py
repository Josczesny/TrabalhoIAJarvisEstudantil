import pytest
from unittest.mock import patch, MagicMock
import numpy as np


class TestChunking:
    def test_chunk_tamanho_fixo(self):
        from jarvis.rag import chunk_texto
        texto = 'A' * 500
        chunks = chunk_texto(texto, tamanho=200, overlap=30)
        assert len(chunks) > 1
        assert all(len(c) <= 200 for c in chunks)

    def test_chunk_overlap(self):
        from jarvis.rag import chunk_texto
        texto = 'abcdefghij' * 30  # 300 chars
        chunks = chunk_texto(texto, tamanho=100, overlap=20)
        # Com overlap, deve haver mais chunks do que sem
        chunks_sem = chunk_texto(texto, tamanho=100, overlap=0)
        assert len(chunks) >= len(chunks_sem)

    def test_chunk_texto_curto(self):
        from jarvis.rag import chunk_texto
        # Texto com mais de 30 chars fica num único chunk
        texto = 'A' * 50
        chunks = chunk_texto(texto, tamanho=200, overlap=30)
        assert len(chunks) == 1

    def test_chunk_descarta_muito_curtos(self):
        from jarvis.rag import chunk_texto
        # Fragmento menor que 30 chars não deve entrar
        texto = 'A' * 200 + ' ' + 'x'  # segundo chunk seria 'x' (1 char)
        chunks = chunk_texto(texto, tamanho=200, overlap=0)
        assert not any(len(c) < 30 for c in chunks)

    def test_chunk_texto_vazio(self):
        from jarvis.rag import chunk_texto
        assert chunk_texto('') == []


class TestRAGBusca:
    def test_busca_sem_index_retorna_vazio(self):
        from jarvis.rag import JARVIS_RAG
        rag = JARVIS_RAG()
        assert rag.buscar('qualquer coisa') == []

    def test_carregar_documentos_indexa_chunks(self, tmp_path):
        from jarvis.rag import JARVIS_RAG
        (tmp_path / 'doc.txt').write_text(
            'Regressão logística usa função sigmoide para classificação binária. '
            'O treinamento minimiza a binary cross-entropy loss com gradiente descendente.',
            encoding='utf-8'
        )
        rag = JARVIS_RAG()
        rag.carregar_documentos(str(tmp_path))
        assert rag.index is not None
        assert len(rag.chunks) > 0

    def test_busca_retorna_chunk_relevante(self, tmp_path):
        from jarvis.rag import JARVIS_RAG
        (tmp_path / 'ml.txt').write_text(
            'Regressão logística é usada para classificação. '
            'A função sigmoide transforma a saída em probabilidade entre 0 e 1.',
            encoding='utf-8'
        )
        rag = JARVIS_RAG()
        rag.carregar_documentos(str(tmp_path))
        resultados = rag.buscar('regressão logística', k=1)
        assert len(resultados) == 1
        assert 'arquivo' in resultados[0]
        assert 'score' in resultados[0]
        assert resultados[0]['score'] > 0
