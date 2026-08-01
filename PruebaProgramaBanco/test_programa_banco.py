import unittest

from Programa_Banco import CuentaMonetaria, convertir_moneda, TASAS_CAMBIO_USD


class TestProgramaBanco(unittest.TestCase):
    def test_convertir_moneda_valida(self):
        self.assertEqual(convertir_moneda(100, "USD", "EUR"), 92.0)
        self.assertEqual(convertir_moneda(100, "EUR", "USD"), 108.7)
        self.assertEqual(convertir_moneda(100, "GTQ", "MXN"), 225.81)

    def test_convertir_moneda_divisa_no_soportada(self):
        with self.assertRaises(ValueError):
            convertir_moneda(100, "USD", "ABC")

    def test_deposito_y_retiro_con_conversion(self):
        cuenta = CuentaMonetaria("CTA-TEST-01", "Tester", "GTQ", 1000.0)
        saldo_despues = cuenta.depositar(100, "USD")
        self.assertEqual(saldo_despues, 1000.0 + 775.0)

        saldo_despues = cuenta.retirar(50, "USD")
        self.assertEqual(saldo_despues, 1775.0 - 387.5)

    def test_retiro_fondo_insuficiente(self):
        cuenta = CuentaMonetaria("CTA-TEST-02", "Tester", "USD", 100.0)
        with self.assertRaises(ValueError):
            cuenta.retirar(200, "USD")

    def test_transferencia_entre_cuentas_diferentes_divisas(self):
        cuenta_origen = CuentaMonetaria("CTA-TEST-03", "Origen", "USD", 500.0)
        cuenta_destino = CuentaMonetaria("CTA-TEST-04", "Destino", "EUR", 100.0)

        cuenta_origen.transferir(cuenta_destino, 100.0, "USD")

        self.assertEqual(cuenta_origen.saldo, 400.0)
        self.assertEqual(cuenta_destino.saldo, 100.0 + 92.0)

    def test_historial_registra_operaciones(self):
        cuenta = CuentaMonetaria("CTA-TEST-05", "Historial", "MXN", 1000.0)
        cuenta.depositar(50, "USD")
        cuenta.retirar(20, "USD")

        historial = cuenta.obtener_historial()
        self.assertEqual(len(historial), 3)
        self.assertEqual(historial[0]["tipo"], "APERTURA")
        self.assertEqual(historial[1]["tipo"], "DEPOSITO")
        self.assertEqual(historial[2]["tipo"], "RETIRO")


if __name__ == "__main__":
    unittest.main()
