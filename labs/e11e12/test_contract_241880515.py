import copy
import json
import unittest
from pathlib import Path

import pipeline


class StudentContract241880515(unittest.TestCase):
    def test_stale_report_rejected_before_repair(self):
        """正确目标报告通过；同一报告改成旧提交后必须拒绝。"""
        root = Path(__file__).resolve().parents[2]
        evidence = root / "work/e12-02"
        report_path = evidence / "incremental-check.json"

        if report_path.exists():
            report = json.loads(report_path.read_text())
            result = json.loads((evidence / "result.json").read_text())
            target = result["target_commit"]
            base = result["base_commit"]
        else:
            # CI 中不依赖个人 work 目录。
            target, base = "b" * 40, "a" * 40
            report = {
                "schema_version": "e11e12-1",
                "kind": "incremental-check",
                "commit": target,
                "status": "SUCCEEDED",
            }

        self.assertNotEqual(base, target)
        pipeline.check_envelope(report, target, "incremental-check")

        stale = copy.deepcopy(report)
        stale["commit"] = base

        with self.assertRaises(pipeline.Failure) as caught:
            pipeline.check_envelope(stale, target, "incremental-check")

        self.assertEqual(caught.exception.code, "STALE_REPORT")
        self.assertEqual(report["commit"], target)

        if report_path.exists():
            output = root / "work/contract-241880515"
            output.mkdir(parents=True, exist_ok=True)
            (output / "stale-report.json").write_text(
                json.dumps(stale, ensure_ascii=False, indent=2)
            )
            (output / "stale-result.json").write_text(
                json.dumps({
                    "expected_error": "STALE_REPORT",
                    "actual_error": caught.exception.code,
                    "report_commit": base,
                    "target_commit": target,
                    "passed": True,
                }, indent=2)
            )


if __name__ == "__main__":
    unittest.main()
