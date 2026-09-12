"""
Unit Tests for Security Validation and Dangerous Action Safeguards.
Developed by G.Vijay Raj (vijay smart).
"""

import unittest
from actions.action_executor import action_executor
from app.config import config
from security.dangerous_actions import DangerousActionManager
from security.validator import SecurityValidator


class TestSecurity(unittest.TestCase):

    def setUp(self):
        config.security.dry_run_mode = True

    def test_path_traversal_rejection(self):
        validator = SecurityValidator()
        self.assertFalse(validator.validate_file_path("../../Windows/System32/calc.exe"))
        self.assertFalse(validator.validate_file_path("C:/Users/../Windows/cmd.exe"))

    def test_dangerous_process_blacklist(self):
        validator = SecurityValidator()
        self.assertFalse(validator.is_executable_safe("format.exe"))
        self.assertFalse(validator.is_executable_safe("vssadmin.exe"))
        self.assertFalse(validator.is_executable_safe("powershell.exe -enc ..."))
        self.assertTrue(validator.is_executable_safe("notepad.exe"))
        self.assertTrue(validator.is_executable_safe("calc.exe"))

    def test_dangerous_action_confirmation_workflow(self):
        manager = DangerousActionManager()
        decisions = []

        def _callback(decision: bool):
            decisions.append(decision)

        # 1. Request confirmation
        manager.request_confirmation("SHUTDOWN_COMPUTER", "Test shutdown", {}, _callback)
        self.assertTrue(manager.has_pending)

        # 2. Reject
        manager.resolve_confirmation(False)
        self.assertFalse(manager.has_pending)
        self.assertEqual(decisions, [False])

        # 3. Request and approve
        manager.request_confirmation("RESTART_COMPUTER", "Test restart", {}, _callback)
        manager.resolve_confirmation(True)
        self.assertEqual(decisions, [False, True])

    def test_unconfirmed_dangerous_action_rejected_by_executor(self):
        config.security.require_confirmation_for_dangerous = True
        config.security.allow_advanced_automation = False

        # Attempt to run SHUTDOWN_COMPUTER without user_confirmed=True
        res = action_executor.execute("SHUTDOWN_COMPUTER", {}, user_confirmed=False)
        self.assertFalse(res.success)
        self.assertIn("confirmation", res.message.lower())


if __name__ == "__main__":
    unittest.main()
