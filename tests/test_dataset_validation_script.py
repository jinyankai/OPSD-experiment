from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DatasetValidationScriptTest(unittest.TestCase):
    def test_script_records_no_offline_preprocessing_decision(self):
        text = (ROOT / "scripts/validate_datasets.py").read_text(encoding="utf-8")
        self.assertIn('"preprocessing_required": False', text)
        self.assertIn("data_collator.py", text)

    def test_train_schema_covers_opsd_and_grpo_fields(self):
        text = (ROOT / "scripts/validate_datasets.py").read_text(encoding="utf-8")
        self.assertIn('"problem"', text)
        self.assertIn('"solution"', text)
        self.assertIn('"Question"', text)
        self.assertIn('"Answer"', text)


if __name__ == "__main__":
    unittest.main()
