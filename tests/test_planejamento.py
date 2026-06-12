import datetime
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.fixture
def tmp_data(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'data').mkdir()
    (tmp_path / 'data' / 'documentos').mkdir()

    hoje = datetime.date.today()
    eventos = [
        {'id': 1, 'titulo': 'Prova de BD', 'tipo': 'prova', 'data': str(hoje + datetime.timedelta(days=3)),
         'horario': '08:00', 'local': 'S1', 'descricao': 'Normalização e ACID'},
    ]
    tarefas = [
        {'id': 1, 'titulo': 'Revisar SQL', 'descricao': '', 'prazo': str(hoje + datetime.timedelta(days=2)),
         'concluida': False, 'prioridade': 'alta'},
        {'id': 2, 'titulo': 'Tarefa concluída', 'descricao': '', 'prazo': str(hoje + datetime.timedelta(days=1)),
         'concluida': True, 'prioridade': 'baixa'},
    ]
    (tmp_path / 'data' / 'agenda.json').write_text(json.dumps(eventos, ensure_ascii=False), encoding='utf-8')
    (tmp_path / 'data' / 'tarefas.json').write_text(json.dumps(tarefas, ensure_ascii=False), encoding='utf-8')
    return tmp_path


class TestPlanejarEstudos:
    def test_inclui_prova_proxima(self, tmp_data):
        from jarvis.tools import planejar_estudos
        # rag.buscar pode retornar vazio sem documentos — ok
        with patch('jarvis.tools.rag') as mock_rag:
            mock_rag.buscar.return_value = []
            resultado = planejar_estudos(dias=7)
        assert 'Prova de BD' in resultado

    def test_inclui_tarefa_pendente(self, tmp_data):
        from jarvis.tools import planejar_estudos
        with patch('jarvis.tools.rag') as mock_rag:
            mock_rag.buscar.return_value = []
            resultado = planejar_estudos(dias=7)
        assert 'Revisar SQL' in resultado

    def test_exclui_tarefa_concluida(self, tmp_data):
        from jarvis.tools import planejar_estudos
        with patch('jarvis.tools.rag') as mock_rag:
            mock_rag.buscar.return_value = []
            resultado = planejar_estudos(dias=7)
        assert 'Tarefa concluída' not in resultado

    def test_sem_eventos_no_periodo(self, tmp_data):
        from jarvis.tools import planejar_estudos
        with patch('jarvis.tools.rag') as mock_rag:
            mock_rag.buscar.return_value = []
            resultado = planejar_estudos(dias=1)
        assert 'Nenhuma prova' in resultado

    def test_materia_chama_rag(self, tmp_data):
        from jarvis.tools import planejar_estudos
        with patch('jarvis.tools.rag') as mock_rag:
            mock_rag.buscar.return_value = [
                {'texto': 'Banco de dados relacional com SQL', 'arquivo': 'banco_de_dados.txt', 'score': 0.9}
            ]
            resultado = planejar_estudos(materia='banco de dados', dias=7)
        mock_rag.buscar.assert_called_once()
        assert 'banco de dados' in resultado.lower() or 'BANCO' in resultado
