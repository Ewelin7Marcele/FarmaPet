"""Testes unitários dos cálculos matemáticos do FarmaPet."""
import unittest
from farmacologia import calcular_quantidade


class TestCalculoDose(unittest.TestCase):
    def test_solucao_mg_ml(self):
        r = calcular_quantidade(5, 10, "mg/kg por administração", 1, "mg/mL", 20)
        self.assertAlmostEqual(r["mg_por_administracao"], 50)
        self.assertAlmostEqual(r["quantidade_por_administracao"], 2.5)
        self.assertEqual(r["unidade"], "mL")

    def test_suspensao_mg_por_5ml(self):
        r = calcular_quantidade(4, 2, "mg/kg por administração", 1, "mg/5 mL", 20)
        self.assertAlmostEqual(r["quantidade_por_administracao"], 2)

    def test_comprimido(self):
        r = calcular_quantidade(6, 5, "mg/kg por administração", 1, "mg/comprimido", 30)
        self.assertAlmostEqual(r["quantidade_por_administracao"], 1)
        self.assertEqual(r["unidade"], "comprimido(s)")

    def test_dose_diaria_dividida(self):
        r = calcular_quantidade(8, 4, "mg/kg por dia", 2, "mg/mL", 16)
        self.assertAlmostEqual(r["total_diario_mg"], 32)
        self.assertAlmostEqual(r["mg_por_administracao"], 16)
        self.assertAlmostEqual(r["quantidade_por_administracao"], 1)


    def test_suspensao_mg_5ml_com_dose_diaria_dividida(self):
        r = calcular_quantidade(5, 10, "mg/kg por dia", 2, "mg/5 mL", 25)
        self.assertAlmostEqual(r["total_diario_mg"], 50)
        self.assertAlmostEqual(r["mg_por_administracao"], 25)
        # 25 mg/5 mL = 5 mg/mL; 25 mg por administração = 5 mL.
        self.assertAlmostEqual(r["quantidade_por_administracao"], 5)
        self.assertAlmostEqual(r["quantidade_diaria"], 10)

    def test_comprimido_com_dose_diaria_dividida(self):
        r = calcular_quantidade(10, 3, "mg/kg por dia", 3, "mg/comprimido", 30)
        self.assertAlmostEqual(r["total_diario_mg"], 30)
        self.assertAlmostEqual(r["mg_por_administracao"], 10)
        self.assertAlmostEqual(r["quantidade_por_administracao"], 1/3)
        self.assertAlmostEqual(r["quantidade_diaria"], 1)

    def test_solucao_dose_por_administracao(self):
        r = calcular_quantidade(2, 4, "mg/kg por administração", 2, "mg/mL", 8)
        self.assertAlmostEqual(r["mg_por_administracao"], 8)
        self.assertAlmostEqual(r["quantidade_por_administracao"], 1)

    def test_rejeita_peso_zero(self):
        with self.assertRaises(ValueError):
            calcular_quantidade(0, 5, "mg/kg por administração", 1, "mg/mL", 10)

    def test_rejeita_frequencia_fracionaria(self):
        with self.assertRaises(ValueError):
            calcular_quantidade(5, 2, "mg/kg por dia", 1.5, "mg/mL", 10)


if __name__ == "__main__":
    unittest.main()
