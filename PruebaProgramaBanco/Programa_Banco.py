import logging
import sys
from datetime import datetime
from typing import Dict, List, Any

# 1. Configuración del sistema de registros (Logging)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ==========================================
# CONFIGURACIÓN Y VALIDADOR DE DIVISAS
# ==========================================

# Tasas de cambio base respecto al Dólar (USD) como moneda de referencia
TASAS_CAMBIO_USD: Dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,
    "GTQ": 7.75,
    "MXN": 17.50
}

def convertir_moneda(monto: float, origen: str, destino: str) -> float:
    """Convierte un monto entre divisas con validación estricta de tipos."""
    if origen not in TASAS_CAMBIO_USD or destino not in TASAS_CAMBIO_USD:
        raise ValueError(f"Divisa no soportada. Soportadas: {list(TASAS_CAMBIO_USD.keys())}")
    
    # Convertir primero a USD (base) y luego a la moneda destino
    monto_usd = monto / TASAS_CAMBIO_USD[origen]
    monto_final = monto_usd * TASAS_CAMBIO_USD[destino]
    return round(monto_final, 2)

# ==========================================
# ESTRUCTURA DE AUDITORÍA
# ==========================================

class TransaccionAuditoria:
    """Clase inmutable para registrar transacciones sin riesgo de alteración."""
    def __init__(self, tipo: str, monto: float, moneda: str, detalle: str, exito: bool):
        self.id_transaccion: int = id(self)  # Identificador único en memoria
        self.fecha_hora: datetime = datetime.now()
        self.tipo: str = tipo               # DEPOSITO, RETIRO, TRANSFERENCIA
        self.monto: float = float(monto)
        self.moneda: str = moneda
        self.detalle: str = detalle
        self.exito: bool = exito

    def a_diccionario(self) -> Dict[str, Any]:
        """Exporta la transacción a un formato plano ideal para depuración."""
        return {
            "id": self.id_transaccion,
            "fecha": self.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": self.tipo,
            "monto": self.monto,
            "moneda": self.moneda,
            "detalle": self.detalle,
            "estado": "EXITOSO" if self.exito else "FALLIDO"
        }

# ==========================================
# LÓGICA DE NEGOCIO (Cuenta Multimoneda)
# ==========================================

class CuentaMonetaria:
    def __init__(self, numero_cuenta: str, titular: str, moneda: str, saldo_inicial: float = 0.0):
        # Validaciones de Tipo
        if not isinstance(numero_cuenta, str) or not numero_cuenta.strip():
            raise TypeError("El número de cuenta debe ser un texto no vacío.")
        if not isinstance(titular, str) or not titular.strip():
            raise TypeError("El nombre del titular debe ser un texto no vacío.")
        if moneda not in TASAS_CAMBIO_USD:
            raise ValueError(f"Moneda '{moneda}' no soportada por el sistema.")
        if not isinstance(saldo_inicial, (int, float)):
            raise TypeError("El saldo inicial debe ser un número.")
        if saldo_inicial < 0:
            raise ValueError("El saldo inicial no puede ser negativo.")

        self.numero_cuenta: str = numero_cuenta.strip()
        self.titular: str = titular.strip()
        self.moneda: str = moneda
        self._saldo: float = float(saldo_inicial)
        
        # Historial de auditoría privado de la cuenta
        self._historial: List[TransaccionAuditoria] = []
        
        logger.info(f"Cuenta {self.numero_cuenta} ({self.moneda}) creada para {self.titular}.")
        self._registrar_auditoria("APERTURA", self._saldo, self.moneda, "Apertura de cuenta", True)

    @property
    def saldo(self) -> float:
        return self._saldo

    def obtener_historial(self) -> List[Dict[str, Any]]:
        """Retorna el historial de auditoría legible para reportes o debuggers."""
        return [t.a_diccionario() for t in self._historial]

    def _registrar_auditoria(self, tipo: str, monto: float, moneda: str, detalle: str, exito: bool):
        """Método interno para asegurar que siempre se registre el evento."""
        log_item = TransaccionAuditoria(tipo, monto, moneda, detalle, exito)
        self._historial.append(log_item)

    def depositar(self, monto: float, moneda_deposito: str) -> float:
        """Deposita dinero aplicando conversión automática si las monedas difieren."""
        try:
            if not isinstance(monto, (int, float)) or monto <= 0:
                raise ValueError("El monto a depositar debe ser un número mayor a cero.")
            if moneda_deposito not in TASAS_CAMBIO_USD:
                raise ValueError(f"Moneda de depósito '{moneda_deposito}' no válida.")

            # Conversión de divisas si es necesario
            monto_convertido = convertir_moneda(monto, moneda_deposito, self.moneda)
            self._saldo += monto_convertido
            
            detalle = f"Depósito recibido de {monto} {moneda_deposito} (Convertido a {monto_convertido} {self.moneda})"
            self._registrar_auditoria("DEPOSITO", monto, moneda_deposito, detalle, True)
            
            logger.info(f"[{self.numero_cuenta}] {detalle}. Nuevo saldo: {self._saldo} {self.moneda}")
            return self._saldo

        except Exception as e:
            self._registrar_auditoria("DEPOSITO", monto, moneda_deposito, f"Fallo: {str(e)}", False)
            raise e

    def retirar(self, monto: float, moneda_retiro: str) -> float:
        """Retira dinero validando fondos suficientes tras la conversión de divisa."""
        try:
            if not isinstance(monto, (int, float)) or monto <= 0:
                raise ValueError("El monto a retirar debe ser un número mayor a cero.")
            if moneda_retiro not in TASAS_CAMBIO_USD:
                raise ValueError(f"Moneda de retiro '{moneda_retiro}' no válida.")

            # Calcular cuánto equivale el retiro en la moneda de la cuenta
            monto_convertido = convertir_moneda(monto, moneda_retiro, self.moneda)
            
            if monto_convertido > self._saldo:
                raise ValueError(f"Fondos insuficientes. Requiere {monto_convertido} {self.moneda}, Disponible: {self._saldo} {self.moneda}")

            self._saldo -= monto_convertido
            detalle = f"Retiro efectuado de {monto} {moneda_retiro} (Cargado {monto_convertido} {self.moneda})"
            self._registrar_auditoria("RETIRO", monto, moneda_retiro, detalle, True)
            
            logger.info(f"[{self.numero_cuenta}] {detalle}. Nuevo saldo: {self._saldo} {self.moneda}")
            return self._saldo

        except Exception as e:
            self._registrar_auditoria("RETIRO", monto, moneda_retiro, f"Fallo: {str(e)}", False)
            raise e

    def transferir(self, cuenta_destino: 'CuentaMonetaria', monto: float, moneda_transferencia: str) -> None:
        """Transfiere fondos de manera atómica entre cuentas con monedas diferentes."""
        if not isinstance(cuenta_destino, CuentaMonetaria):
            raise TypeError("La cuenta destino debe ser una instancia de CuentaMonetaria.")
        if cuenta_destino.numero_cuenta == self.numero_cuenta:
            raise ValueError("No se permiten transferencias a la misma cuenta de origen.")

        logger.debug(f"Iniciando transferencia de {self.numero_cuenta} a {cuenta_destino.numero_cuenta}")
        
        # 1. Intentar retirar de la cuenta origen
        # Si falla por fondos insuficientes o datos erróneos, la ejecución se corta aquí de forma segura
        self.retirar(monto, moneda_transferencia)
        
        # 2. Intentar depositar en la cuenta destino
        try:
            cuenta_destino.depositar(monto, moneda_transferencia)
            
            detalle_origen = f"Transferencia enviada a Cuenta {cuenta_destino.numero_cuenta}. Monto: {monto} {moneda_transferencia}"
            # Actualizamos el último registro de retiro con más contexto
            self._historial[-1].detalle = detalle_origen
            
            logger.info(f"Transferencia internacional exitosa: {self.numero_cuenta} -> {cuenta_destino.numero_cuenta}")
            
        except Exception as e:
            # INTERRUPCIÓN CONTROLADA (Rollback): Si el depósito falla por cualquier anomalía,
            # devolvemos el dinero exacto cobrado a la cuenta origen para que no se pierda el balance.
            monto_convertido_origen = convertir_moneda(monto, moneda_transferencia, self.moneda)
            self._saldo += monto_convertido_origen
            
            # Registrar el colapso en ambas cuentas para auditoría de sistemas
            msg_error = f"ROLLBACK: Transferencia falló en destino. Dinero reintegrado. Error: {e}"
            self._registrar_auditoria("SISTEMA_REVERTIDO", monto, moneda_transferencia, msg_error, False)
            cuenta_destino._registrar_auditoria("TRANSFERENCIA_RECHAZADA", monto, moneda_transferencia, f"Rechazado: {e}", False)
            
            logger.critical(f"Error crítico en transferencia. {msg_error}")
            raise RuntimeError("Transacción cancelada de forma segura debido a fallos en el destino.") from e

# ==========================================
# BANCO TOTAL (Base de Datos en Memoria)
# ==========================================

def main():
    logger.info("Iniciando Sistema de Control Monetario Multimoneda.")
    banco: Dict[str, CuentaMonetaria] = {}

    try:
        # Registro inicial de cuentas en diferentes monedas
        banco["CTA-USD-01"] = CuentaMonetaria("CTA-USD-01", "Alice Smith", "USD", 1000.0)
        banco["CTA-GTQ-02"] = CuentaMonetaria("CTA-GTQ-02", "Bernardo Méndez", "GTQ", 5000.0)
        banco["CTA-EUR-03"] = CuentaMonetaria("CTA-EUR-03", "Chloe Dubois", "EUR", 100.0)

        # ----------------------------------------------------
        # Batería de Pruebas de Estrés para Debugging
    except Exception as e:
        logger.error(f"Error en la ejecución principal: {e}")
        raise
