import json
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch


@pytest.fixture
def tmp_data(tmp_path, monkeypatch):
    """Redirect data files to a temp directory."""
    agenda = tmp_path / 'agenda.json'
    tarefas = tmp_path / 'tarefas.json'
    agenda.write_text('[]', encoding='utf-8')
    tarefas.write_text('[]', encoding='utf-8')
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'data').mkdir()
    (tmp_path / 'data' / 'agenda.json').write_text('[]', encoding='utf-8')
    (tmp_path / 'data' / 'tarefas.json').write_text('[]', encoding='utf-8')
    (tmp_path / 'data' / 'documentos').mkdir()
    return tmp_path


def _load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


# ── Tarefas ───────────────────────────────────────────────────────────

class TestAdicionarTarefa:
    def test_adiciona_com_campos_minimos(self, tmp_data):
        from jarvis.tools import adicionar_tarefa
        resultado = adicionar_tarefa('Estudar redes neurais')
        assert 'Estudar redes neurais' in resultado
        tarefas = _load('data/tarefas.json')
        assert len(tarefas) == 1
        assert tarefas[0]['titulo'] == 'Estudar redes neurais'
        assert tarefas[0]['concluida'] is False

    def test_id_incrementa(self, tmp_data):
        from jarvis.tools import adicionar_tarefa
        adicionar_tarefa('Tarefa A')
        adicionar_tarefa('Tarefa B')
        tarefas = _load('data/tarefas.json')
        ids = [t['id'] for t in tarefas]
        assert ids == [1, 2]

    def test_prioridade_customizada(self, tmp_data):
        from jarvis.tools import adicionar_tarefa
        adicionar_tarefa('Urgente', prioridade='alta')
        tarefas = _load('data/tarefas.json')
        assert tarefas[0]['prioridade'] == 'alta'

    def test_prazo_customizado(self, tmp_data):
        from jarvis.tools import adicionar_tarefa
        adicionar_tarefa('Com prazo', prazo='2030-12-31')
        tarefas = _load('data/tarefas.json')
        assert tarefas[0]['prazo'] == '2030-12-31'


class TestListarTarefas:
    def test_lista_apenas_pendentes(self, tmp_data):
        from jarvis.tools import adicionar_tarefa, concluir_tarefa, listar_tarefas
        adicionar_tarefa('Pendente')
        adicionar_tarefa('Concluida')
        concluir_tarefa(2)
        resultado = listar_tarefas(apenas_pendentes=True)
        assert 'Pendente' in resultado
        assert 'Concluida' not in resultado

    def test_lista_todas(self, tmp_data):
        from jarvis.tools import adicionar_tarefa, concluir_tarefa, listar_tarefas
        adicionar_tarefa('Pendente')
        adicionar_tarefa('Concluida')
        concluir_tarefa(2)
        resultado = listar_tarefas(apenas_pendentes=False)
        assert 'Pendente' in resultado
        assert 'Concluida' in resultado

    def test_lista_vazia(self, tmp_data):
        from jarvis.tools import listar_tarefas
        resultado = listar_tarefas()
        assert 'Nenhuma' in resultado


class TestConcluirTarefa:
    def test_conclui_existente(self, tmp_data):
        from jarvis.tools import adicionar_tarefa, concluir_tarefa
        adicionar_tarefa('Revisar material')
        resultado = concluir_tarefa(1)
        assert '✓' in resultado or 'concluída' in resultado.lower()
        tarefas = _load('data/tarefas.json')
        assert tarefas[0]['concluida'] is True

    def test_id_inexistente(self, tmp_data):
        from jarvis.tools import concluir_tarefa
        resultado = concluir_tarefa(999)
        assert 'não encontrada' in resultado.lower()

    def test_ja_concluida(self, tmp_data):
        from jarvis.tools import adicionar_tarefa, concluir_tarefa
        adicionar_tarefa('Dupla conclusão')
        concluir_tarefa(1)
        resultado = concluir_tarefa(1)
        assert 'já' in resultado.lower()

    def test_id_invalido(self, tmp_data):
        from jarvis.tools import concluir_tarefa
        resultado = concluir_tarefa('abc')
        assert 'inválido' in resultado.lower() or 'inv' in resultado.lower()
