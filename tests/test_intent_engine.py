"""
Unit Tests for Intent Recognition and Fallback Parsing.
Developed by G.Vijay Raj (vijay smart).
"""

import unittest
from ai.fallback_engine import fallback_engine
from ai.schemas import IntentResult
from core.intent_engine import intent_engine
from utils.validation import parse_json_safely


class TestIntentEngine(unittest.TestCase):

    def test_offline_volume_commands(self):
        result = fallback_engine.parse("Turn the volume down to 40")
        self.assertIsNotNone(result)
        self.assertEqual(result.intent, "SET_VOLUME")
        self.assertEqual(result.parameters.get("value"), 40)

        result_mute = fallback_engine.parse("Mute audio")
        self.assertIsNotNone(result_mute)
        self.assertEqual(result_mute.intent, "MUTE_VOLUME")

    def test_offline_application_commands(self):
        res = fallback_engine.parse("Open Chrome")
        self.assertIsNotNone(res)
        self.assertEqual(res.intent, "OPEN_APPLICATION")
        self.assertEqual(res.target, "chrome")

        res_close = fallback_engine.parse("Close notepad")
        self.assertIsNotNone(res_close)
        self.assertEqual(res_close.intent, "CLOSE_APPLICATION")
        self.assertEqual(res_close.target, "notepad")

    def test_offline_telemetry_commands(self):
        res_cpu = fallback_engine.parse("What is my CPU usage?")
        self.assertIsNotNone(res_cpu)
        self.assertEqual(res_cpu.intent, "GET_CPU_USAGE")

        res_ram = fallback_engine.parse("How much RAM am I using?")
        self.assertIsNotNone(res_ram)
        self.assertEqual(res_ram.intent, "GET_MEMORY_USAGE")

    def test_offline_dangerous_commands_flag_confirmation(self):
        res_shut = fallback_engine.parse("Shutdown computer")
        self.assertIsNotNone(res_shut)
        self.assertEqual(res_shut.intent, "SHUTDOWN_COMPUTER")
        self.assertTrue(res_shut.requires_confirmation)

    def test_malformed_ai_json_parsing(self):
        # Test invalid JSON safely recovers None
        bad_json = "This is not json at all"
        parsed = parse_json_safely(bad_json)
        self.assertIsNone(parsed)

        # Test markdown code block extraction
        md_json = "```json\n{\"intent\": \"OPEN_APPLICATION\", \"target\": \"notepad\"}\n```"
        parsed_md = parse_json_safely(md_json)
        self.assertIsNotNone(parsed_md)
        self.assertEqual(parsed_md["intent"], "OPEN_APPLICATION")

        # Test IntentResult handles malformed dict
        intent_obj = IntentResult.from_dict({"not_an_intent": 123})
        self.assertIsNone(intent_obj)

    def test_unknown_command_fallback(self):
        res = intent_engine.parse_intent("xyz123 random gibberish phrase")
        self.assertIsNotNone(res)
        # Low confidence or conversational demotion
        self.assertIn(res.intent, ["CONVERSATION", "UNKNOWN"])


if __name__ == "__main__":
    unittest.main()
