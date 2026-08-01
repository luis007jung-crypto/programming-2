import logging
import sys
import argparse
import random
from typing import Dict

from Programa_Banco import CuentaMonetaria, TASAS_CAMBIO_USD

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

class BancoCLI:
    def __init__(self):
        self.cuentas: Dict[str, CuentaMonetaria] = {}

    def _generar_numero_cuenta(self) -> str:
        while True:
            numero = ''.join(str(random.randint(0, 9)) for _ in range(10))
            if numero not in self.cuentas:
                return numero

    def _existe_titular_misma_moneda(self, titular: str, moneda: str) -> bool:
        return any(c.titular == titular and c.moneda == moneda for c in self.cuentas.values())

    def crear_cuenta(self):
        titular = input("Titular: ").strip()
        moneda = input(f"Moneda ({', '.join(TASAS_CAMBIO_USD.keys())}): ").strip().upper()
        if self._existe_titular_misma_moneda(titular, moneda):
            logger.error(
                "Ya existe una cuenta para este titular con la misma moneda. "
                "Use una moneda diferente para registrar otra cuenta. "
                f"Monedas válidas: {', '.join(TASAS_CAMBIO_USD.keys())}"
            )
            return

        saldo = input("Saldo inicial (número): ").strip()
        try:
            saldo_val = float(saldo) if saldo else 0.0
            numero = self._generar_numero_cuenta()
            cuenta = CuentaMonetaria(numero, titular, moneda, saldo_val)
            self.cuentas[cuenta.numero_cuenta] = cuenta
            logger.info("Cuenta creada correctamente. Detalles:")
            logger.info(f"  Número de cuenta: {cuenta.numero_cuenta}")
            logger.info(f"  Titular: {cuenta.titular}")
            logger.info(f"  Tipo de moneda: {cuenta.moneda}")
            logger.info(f"  Saldo inicial: {cuenta.saldo}")
        except Exception as e:
            logger.error(f"Error al crear cuenta: {e}")

    def listar_cuentas(self):
        if not self.cuentas:
            logger.info("No hay cuentas registradas.")
            return
        for num, c in self.cuentas.items():
            logger.info(f"{num}: {c.titular} - {c.saldo} {c.moneda}")

    def depositar(self):
        num = input("Cuenta destino: ").strip()
        if num not in self.cuentas:
            logger.error("Cuenta no encontrada.")
            return
        monto = input("Monto a depositar: ").strip()
        moneda = input("Moneda del depósito: ").strip().upper()
        try:
            m = float(monto)
            nuevo = self.cuentas[num].depositar(m, moneda)
            logger.info(f"Nuevo saldo: {nuevo} {self.cuentas[num].moneda}")
        except Exception as e:
            logger.error(f"Error en depósito: {e}")

    def retirar(self):
        num = input("Cuenta origen: ").strip()
        if num not in self.cuentas:
            logger.error("Cuenta no encontrada.")
            return
        monto = input("Monto a retirar: ").strip()
        moneda = input("Moneda del retiro: ").strip().upper()
        try:
            m = float(monto)
            nuevo = self.cuentas[num].retirar(m, moneda)
            logger.info(f"Nuevo saldo: {nuevo} {self.cuentas[num].moneda}")
        except Exception as e:
            logger.error(f"Error en retiro: {e}")

    def transferir(self):
        origen = input("Cuenta origen: ").strip()
        destino = input("Cuenta destino: ").strip()
        if origen not in self.cuentas or destino not in self.cuentas:
            logger.error("Cuenta origen o destino no encontrada.")
            return
        monto = input("Monto a transferir: ").strip()
        moneda = input("Moneda de la transferencia: ").strip().upper()
        try:
            m = float(monto)
            self.cuentas[origen].transferir(self.cuentas[destino], m, moneda)
            logger.info("Transferencia completada.")
        except Exception as e:
            logger.error(f"Error en transferencia: {e}")

    def mostrar_historial(self):
        num = input("Cuenta: ").strip()
        if num not in self.cuentas:
            logger.error("Cuenta no encontrada.")
            return
        historial = self.cuentas[num].obtener_historial()
        for item in historial:
            logger.info(item)

    def run_interactive(self):
        menu = {
            '1': ('Crear cuenta', self.crear_cuenta),
            '2': ('Listar cuentas', self.listar_cuentas),
            '3': ('Depositar', self.depositar),
            '4': ('Retirar', self.retirar),
            '5': ('Transferir', self.transferir),
            '6': ('Mostrar historial', self.mostrar_historial),
            '7': ('Salir', None)
        }
        while True:
            logger.info('\n--- Banco CLI ---')
            for k, v in menu.items():
                logger.info(f"{k}. {v[0]}")
            choice = input("Seleccione una opción: ").strip()
            if choice == '7':
                logger.info("Saliendo...")
                break
            action = menu.get(choice)
            if not action:
                logger.error("Opción inválida.")
                continue
            try:
                action[1]()
            except Exception as e:
                logger.error(f"Error: {e}")

    def run_demo(self):
        # Demo automatizado para verificar comportamiento sin interacción
        logger.info("Ejecutando demo automático...")
        self.cuentas['A1'] = CuentaMonetaria('A1', 'Alice', 'USD', 1000.0)
        self.cuentas['B1'] = CuentaMonetaria('B1', 'Bob', 'EUR', 200.0)
        self.cuentas['C1'] = CuentaMonetaria('C1', 'Carlos', 'GTQ', 1000.0)

        logger.info('Depósito: agregar 100 EUR a A1 (convertido a USD)')
        try:
            self.cuentas['A1'].depositar(100, 'EUR')
        except Exception as e:
            logger.error(e)

        logger.info('Retiro: quitar 50 USD de A1')
        try:
            self.cuentas['A1'].retirar(50, 'USD')
        except Exception as e:
            logger.error(e)

        logger.info('Transferencia: A1 -> B1, 200 USD')
        try:
            self.cuentas['A1'].transferir(self.cuentas['B1'], 200, 'USD')
        except Exception as e:
            logger.error(e)

        logger.info('\nSaldos finales:')
        self.listar_cuentas()


def main():
    parser = argparse.ArgumentParser(description='Interfaz interactiva para el sistema bancario.')
    parser.add_argument('--demo', action='store_true', help='Ejecuta una demo automatizada y sale')
    args = parser.parse_args()

    cli = BancoCLI()
    if args.demo:
        cli.run_demo()
        return
    cli.run_interactive()

if __name__ == '__main__':
    main()
