from datetime import date, timedelta
from regras import calcular_dias_restantes, classificar_obrigacao

def test_dias_restantes_futuro():
    amanha = date.today() + timedelta(days=1)
    assert calcular_dias_restantes(amanha) == 1

def test_obrigacao_atrasada():
    ontem = date.today() - timedelta(days=1)
    assert classificar_obrigacao(ontem, "Pendente") == "Atrasada"

def test_obrigacao_vence_em_5_dias():
    em_5_dias = date.today() + timedelta(days=5)
    assert classificar_obrigacao(em_5_dias, "Pendente") == "Vence em 5 dias"

def test_obrigacao_concluida_nao_alerta():
    ontem = date.today() - timedelta(days=1)
    assert classificar_obrigacao(ontem, "Concluída") == "Concluída"