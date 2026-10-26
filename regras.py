from datetime import date

def calcular_dias_restantes(data_vencimento):
    return (data_vencimento - date.today()).days

def classificar_obrigacao(data_vencimento, status):
    if status == "Concluída":
        return "Concluída"
    dias = calcular_dias_restantes(data_vencimento)
    if dias < 0:
        return "Atrasada"
    if dias <= 7:
        return f"Vence em {dias} dias"
    return "Pendente"