from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass
class Payment:
    id: str
    amount: float
    description: str
    currency: str = "USD"
    status: str = "pending"
    provider_id: Optional[str] = None


class PaymentManager:
    def __init__(self) -> None:
        self._payments: Dict[str, Payment] = {}

    def register_payment(self, amount: float, description: str, currency: str = "USD") -> Payment:
        payment = Payment(id=str(uuid4()), amount=amount, description=description, currency=currency)
        self._payments[payment.id] = payment
        return payment

    def process_payment(self, payment_id: str) -> Payment:
        payment = self._payments[payment_id]
        payment.status = "processed"
        return payment

    def list_payments(self) -> List[Payment]:
        return list(self._payments.values())

    def get_payment(self, payment_id: str) -> Optional[Payment]:
        return self._payments.get(payment_id)


class PaymentIntegrator:
    def __init__(self, provider_id: str) -> None:
        self.provider_id = provider_id

    def sync_payment(self, payment_id: str, manager: PaymentManager) -> Payment:
        payment = manager.get_payment(payment_id)
        if payment is None:
            raise ValueError("Payment not found")

        payment.status = "processed"
        payment.provider_id = self.provider_id
        return payment


def generate_report(payments: List[Payment]) -> Dict[str, float | int]:
    processed_count = sum(1 for p in payments if p.status == "processed")
    total_amount = sum(p.amount for p in payments)

    return {
        "total_count": len(payments),
        "processed_count": processed_count,
        "total_amount": round(total_amount, 2),
    }


if __name__ == "__main__":
    manager = PaymentManager()
    manager.register_payment(120.0, "Membresía mensual")
    manager.register_payment(300.0, "Curso avanzado")
    manager.process_payment(manager.list_payments()[0].id)

    report = generate_report(manager.list_payments())
    print("Reporte de pagos:")
    for key, value in report.items():
        print(f"- {key}: {value}")
