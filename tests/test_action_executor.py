"""
Unit Tests for Action Execution and Simulation.
Developed by G.Vijay Raj (vijay smart).
"""

import unittest
from actions.action_executor import action_executor
from app.config import config


class TestActionExecutor(unittest.TestCase):

    def setUp(self):
        # Enable dry run mode for safety in all tests
        config.security.dry_run_mode = True

    def tearDown(self):
        config.security.dry_run_mode = False

    def test_dry_run_simulation(self):
        res = action_executor.execute("SET_VOLUME", {"value": 50})
        self.assertTrue(res.success)
        self.assertTrue(res.data.get("simulated"))
        self.assertIn("SIMULATION", res.message)

    def test_unknown_action(self):
        res = action_executor.execute("NON_EXISTENT_ACTION_NAME", {})
        self.assertFalse(res.success)
        self.assertIn("unsupported action", res.message.lower())

    def test_system_info_action(self):
        config.security.dry_run_mode = False
        res = action_executor.execute("SYSTEM_INFO", {})
        self.assertTrue(res.success)
        self.assertIn("os", res.data)

    def test_missing_required_parameters(self):
        # OPEN_APPLICATION requires 'target'
        res = action_executor.execute("OPEN_APPLICATION", {})
        self.assertFalse(res.success)
        self.assertIn("required", res.message.lower())


if __name__ == "__main__":
    unittest.main()
