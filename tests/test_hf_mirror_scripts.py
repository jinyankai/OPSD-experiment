from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class HfMirrorScriptTest(unittest.TestCase):
    def test_experiment_scripts_source_hf_mirror_helper(self):
        scripts = [
            "scripts/run_opsd_1b.sh",
            "scripts/run_opsd_4b.sh",
            "scripts/run_opsd_4b_nonthink.sh",
            "scripts/run_opsd_8b.sh",
            "scripts/run_opsd_8b_nonthink.sh",
            "scripts/run_sft.sh",
            "scripts/run_grpo.sh",
            "eval/run_eval.sh",
            "eval/run_eval_nonthink.sh",
        ]
        missing = []
        for relative in scripts:
            text = (ROOT / relative).read_text(encoding="utf-8")
            if "hf_mirror_env.sh" not in text:
                missing.append(relative)
        self.assertEqual([], missing)

    def test_hf_mirror_helper_defaults_to_hf_mirror(self):
        text = (ROOT / "scripts/hf_mirror_env.sh").read_text(encoding="utf-8")
        self.assertIn("https://hf-mirror.com", text)
        self.assertIn("USE_HF_MIRROR", text)
        self.assertIn("HF_ENDPOINT", text)


if __name__ == "__main__":
    unittest.main()
