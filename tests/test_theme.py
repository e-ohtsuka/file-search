"""GUI Design Studioから出力したテーマの簡易検証（GUI実行不要）。"""
import ast
import json
from pathlib import Path
import sys
import unittest

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))


class ThemeTests(unittest.TestCase):
    def test_python_source_compiles(self):
        for name in ('file-search.py', 'design_theme.py'):
            ast.parse((BASE / name).read_text(encoding='utf-8'))

    def test_standard_ttk_mode(self):
        theme = json.loads((BASE / 'design_theme.json').read_text(encoding='utf-8'))
        self.assertEqual(theme['render_mode'], 'standard_ttk')
        self.assertFalse(theme['requires_custom'])

    def test_colors_are_valid_hex(self):
        theme = json.loads((BASE / 'design_theme.json').read_text(encoding='utf-8'))
        self.assertTrue(theme['colors'])
        for c in theme['colors'].values():
            self.assertRegex(c, r'^#[0-9A-Fa-f]{6}$')

    def test_exported_colors_match(self):
        from design_theme import THEME
        theme = json.loads((BASE / 'design_theme.json').read_text(encoding='utf-8'))
        self.assertEqual(THEME, theme)


if __name__ == '__main__':
    unittest.main()
