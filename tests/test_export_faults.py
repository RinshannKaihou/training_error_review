import unittest

from tools.export_faults import parse_entries


class ExportFaultsTests(unittest.TestCase):
    def test_discovery_source_stops_at_next_category_heading(self):
        text = """### HW.09 `hardware_fault`

stage: `shared` · Cov: `NEW` · 置信度 `documented`

- **机制**：硬件异常
- **来源**：https://example.com/hw
- **行为效应**：训练偏离
- **发现来源**：2026-09-19 每日扫描

---

# NUM · 数值 / 混精

## NUM

### NUM.01 `numerical_fault`

stage: `shared` · Cov: `NEW` · 置信度 `documented`

- **机制**：数值异常
- **来源**：https://example.com/num
- **行为效应**：训练偏离
- **发现来源**：2026-09-20 每日扫描
"""
        entries = parse_entries(text)
        self.assertEqual([e["id"] for e in entries], ["HW.09", "NUM.01"])
        self.assertEqual(entries[0]["discovery_date"], "2026-09-19 每日扫描")
        self.assertEqual(entries[1]["discovery_date"], "2026-09-20 每日扫描")


if __name__ == "__main__":
    unittest.main()
