import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modulo_pagos import PaymentManager, generate_report, PaymentIntegrator


class PaymentModuleTests(unittest.TestCase):
    def test_register_and_process_payment(self):
        manager = PaymentManager()
        payment = manager.register_payment(150.0, "Curso Python", currency="USD")

        self.assertEqual(payment.status, "pending")

        processed = manager.process_payment(payment.id)
        self.assertEqual(processed.status, "processed")
        self.assertEqual(processed.amount, 150.0)

    def test_generate_report_summary(self):
        manager = PaymentManager()
        manager.register_payment(100.0, "Plan básico")
        manager.register_payment(250.0, "Plan premium")
        manager.process_payment(manager.list_payments()[0].id)

        report = generate_report(manager.list_payments())

        self.assertEqual(report["total_count"], 2)
        self.assertEqual(report["processed_count"], 1)
        self.assertEqual(report["total_amount"], 350.0)

    def test_integration_sync_updates_status(self):
        manager = PaymentManager()
        payment = manager.register_payment(50.0, "Suscripción")
        integrator = PaymentIntegrator("mock-gateway")

        synced = integrator.sync_payment(payment.id, manager)

        self.assertEqual(synced.status, "processed")
        self.assertEqual(synced.provider_id, "mock-gateway")


if __name__ == "__main__":
    unittest.main()
