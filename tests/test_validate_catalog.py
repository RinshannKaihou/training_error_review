import unittest
from tools.validate_catalog import check_rows


class ExportValidationTest(unittest.TestCase):
    def test_rejects_markdown_heading_inside_discovery_date(self):
        with self.assertRaisesRegex(ValueError, "discovery_date"):
            check_rows([{"id": "CKPT.28", "discovery_date": "2026-09-23\n# DATA"}])


if __name__ == "__main__":
    unittest.main()
