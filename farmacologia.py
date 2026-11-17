"""Funções matemáticas isoladas para os cálculos do FarmaPet.

Este módulo não contém doses terapêuticas recomendadas. Os valores devem vir
exclusivamente de uma prescrição veterinária válida.
"""
from math import isfinite


def calcular_quantidade(peso_kg, dose_mg_kg, base, frequencia_dia, apresentacao, teor):
    """Calcula a quantidade matemática por administração.

    Bases aceitas: 'mg/kg por administração' ou 'mg/kg por dia'.
    Apresentações aceitas: 'mg/mL', 'mg/5 mL' e 'mg/comprimido'.
    """
    valores = (peso_kg, dose_mg_kg, teor)
    if not all(isfinite(float(v)) and float(v) > 0 for v in valores):
        raise ValueError("Peso, dose e teor/concentração devem ser números positivos e finitos.")

    peso_kg, dose_mg_kg, teor = map(float, valores)
    total_diario_mg = None
    if base == "mg/kg por dia":
        if not isinstance(frequencia_dia, int) or not 1 <= frequencia_dia <= 24:
            raise ValueError("Para dose diária, informe de 1 a 24 administrações inteiras por dia.")
        total_diario_mg = dose_mg_kg * peso_kg
        mg_por_administracao = total_diario_mg / frequencia_dia
    elif base == "mg/kg por administração":
        mg_por_administracao = dose_mg_kg * peso_kg
    else:
        raise ValueError("Base de dose não reconhecida.")

    if apresentacao == "mg/mL":
        quantidade = mg_por_administracao / teor
        unidade = "mL"
        quantidade_diaria = total_diario_mg / teor if total_diario_mg is not None else None
    elif apresentacao == "mg/5 mL":
        mg_por_ml = teor / 5.0
        quantidade = mg_por_administracao / mg_por_ml
        unidade = "mL"
        quantidade_diaria = total_diario_mg / mg_por_ml if total_diario_mg is not None else None
    elif apresentacao == "mg/comprimido":
        quantidade = mg_por_administracao / teor
        unidade = "comprimido(s)"
        quantidade_diaria = total_diario_mg / teor if total_diario_mg is not None else None
    else:
        raise ValueError("Apresentação farmacêutica não reconhecida.")

    if not isfinite(quantidade) or quantidade <= 0:
        raise ValueError("Não foi possível calcular. Confira os valores e as unidades.")

    return {
        "mg_por_administracao": mg_por_administracao,
        "quantidade_por_administracao": quantidade,
        "unidade": unidade,
        "total_diario_mg": total_diario_mg,
        "quantidade_diaria": quantidade_diaria,
    }
