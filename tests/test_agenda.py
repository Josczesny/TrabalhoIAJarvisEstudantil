import datetime
import json
import pytest
from pathlib import Path


@pytest.fixture
def tmp_data(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'data').mkdir()
    (tmp_path / 'data' / 'documentos').mkdir()

    hoje = datetime.date.today()
    amanha = str(hoje + datetime.timedelta(days=1))
    semana = str(hoje + datetime.timedelta(days=4))

    eventos = [
        {'id': 1, 'titulo': 'Aula Hoje',   'tipo': 'aula',   'data': str(hoje), 'horario': '08:00', 'local': 'S1', 'descricao': ''},
        {'id': 2, 'titulo': 'Prova Amanhã', 'tipo': 'prova',  'data': amanha,    'horario': '14:00', 'local': 'S2', 'descricao': ''},
        {'id': 3, 'titulo': 'Aula Semana',  'tipo': 'aula',   'data': semana,    'horario': '10:00', 'local': 'S3', 'descricao': ''},
        {'id': 4, 'titulo': 'Entrega',      'tipo': 'entrega','data': amanha,    'horario': '23:59', 'local': 'Online', 'descricao': ''},
    ]
    (tmp_path / 'data' / 'agenda.json').write_text(
        json.dumps(eventos, ensure_ascii=False), encoding='utf-8'
    )
    (tmp_path / 'data' / 'tarefas.json').write_text('[]', encoding='utf-8')
    return tmp_path


class TestConsultarAgenda:
    def test_hoje(self, tmp_data):
        from jarvis.tools import consultar_agenda
        resultado = consultar_agenda(data='hoje')
        assert 'Aula Hoje' in resultado
        assert 'Prova Amanhã' not in resultado

    def test_amanha(self, tmp_data):
        from jarvis.tools import consultar_agenda
        resultado = consultar_agenda(data='amanhã')
        assert 'Prova Amanhã' in resultado
        assert 'Aula Hoje' not in resultado

    def test_semana_inclui_todos(self, tmp_data):
        from jarvis.tools import consultar_agenda
        resultado = consultar_agenda(data='semana')
        assert 'Aula Hoje' in resultado
        assert 'Aula Semana' in resultado

    def test_filtro_tipo(self, tmp_data):
        from jarvis.tools import consultar_agenda
        resultado = consultar_agenda(data='semana', tipo='prova')
        assert 'Prova Amanhã' in resultado
        assert 'Aula Hoje' not in resultado

    def test_nenhum_evento(self, tmp_data):
        from jarvis.tools import consultar_agenda
        resultado = consultar_agenda(data='2000-01-01')
        assert 'Nenhum evento' in resultado


class TestConsultarProvasProximas:
    def test_retorna_prova(self, tmp_data):
        from jarvis.tools import consultar_provas_proximas
        resultado = consultar_provas_proximas(dias=7)
        assert 'Prova Amanhã' in resultado

    def test_nao_retorna_aula(self, tmp_data):
        from jarvis.tools import consultar_provas_proximas
        resultado = consultar_provas_proximas(dias=7)
        assert 'Aula Hoje' not in resultado

    def test_janela_zero_dias(self, tmp_data):
        from jarvis.tools import consultar_provas_proximas
        # eventos de amanhã não entram na janela de 0 dias
        resultado = consultar_provas_proximas(dias=0)
        assert 'Nenhuma' in resultado
