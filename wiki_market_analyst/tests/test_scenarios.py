"""
Automated tests for Wiki Market Analyst skill.
Verifies all 3 core case study scenarios end-to-end:
1. Scenario 1: Intermittent Fasting (pl vs cs).
2. Scenario 2: Astronomy course in Ukrainian Wikipedia (uk).
3. Scenario 3: English language learning across multi-lingual locales (uk, pl, es, de, cs).
"""

import unittest
import os
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from main import run_pipeline

class TestWikiMarketAnalystScenarios(unittest.TestCase):
    
    def setUp(self):
        self.output_base = os.path.join(parent_dir, "..", "output", "test_runs")
        os.makedirs(self.output_base, exist_ok=True)

    def test_scenario_1_intermittent_fasting(self):
        """Scenario 1: Polish vs Czech comparison for Intermittent Fasting over 2 years."""
        out_dir = os.path.join(self.output_base, "scenario_1")
        result = run_pipeline(
            topic="Intermittent fasting",
            langs=["pl", "cs"],
            years=2,
            output_dir=out_dir
        )
        self.assertEqual(result["qid"], "Q1666254")
        self.assertIn("pl", result["markets"])
        self.assertIn("cs", result["markets"])
        
        # Polish article lacks dedicated QID page in pl.wikipedia.org
        self.assertFalse(result["markets"]["pl"]["has_data"])
        
        # Czech article exists and has traffic records
        cs_market = result["markets"]["cs"]
        self.assertTrue(cs_market["has_data"])
        self.assertGreater(cs_market["total_views"], 0)
        self.assertIn("Přerušovaný půst", cs_market["title"])
        self.assertTrue(os.path.exists(result["artifacts"]["chart_png"]))
        self.assertTrue(os.path.exists(result["artifacts"]["report_pdf"]))

    def test_scenario_2_astronomy_ukraine(self):
        """Scenario 2: Astronomy course viability in Ukrainian Wikipedia."""
        out_dir = os.path.join(self.output_base, "scenario_2")
        result = run_pipeline(
            topic="Астрономія",
            langs=["uk"],
            years=2,
            output_dir=out_dir
        )
        self.assertEqual(result["qid"], "Q333")
        uk_market = result["markets"]["uk"]
        self.assertTrue(uk_market["has_data"])
        self.assertGreater(uk_market["total_views"], 5000)
        self.assertEqual(uk_market["trust_level"], "HIGH")
        self.assertTrue(os.path.exists(result["artifacts"]["chart_png"]))
        self.assertTrue(os.path.exists(result["artifacts"]["report_pdf"]))

    def test_scenario_3_english_multi_market(self):
        """Scenario 3: English language learning across multi-lingual locales."""
        out_dir = os.path.join(self.output_base, "scenario_3")
        result = run_pipeline(
            topic="English language",
            langs=["uk", "pl", "es", "de", "cs"],
            years=2,
            output_dir=out_dir
        )
        self.assertEqual(result["qid"], "Q1860")
        for lang in ["uk", "pl", "es", "de", "cs"]:
            self.assertIn(lang, result["markets"])
            self.assertTrue(result["markets"][lang]["has_data"])
            self.assertGreater(result["markets"][lang]["total_views"], 1000)
            
        self.assertTrue(os.path.exists(result["artifacts"]["chart_png"]))
        self.assertTrue(os.path.exists(result["artifacts"]["report_pdf"]))

if __name__ == "__main__":
    unittest.main()
