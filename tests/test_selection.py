"""検索結果の選択表示とTab操作に関する静的回帰テスト。"""
import ast
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / 'file-search.py').read_text(encoding='utf-8')

class SelectionTests(unittest.TestCase):
    def test_tab_focus_is_on_treeview(self):
        syntax = ast.parse(SOURCE)
        handler = next(node for node in syntax.body
                       if isinstance(node, ast.FunctionDef)
                       and node.name == 'funcWordSetTab')
        names = {node.attr for node in ast.walk(handler)
                 if isinstance(node, ast.Attribute)}
        self.assertTrue({'focus', 'selection_set', 'focus_set', 'see'} <= names)
        self.assertTrue(any(isinstance(node, ast.Return)
                            and isinstance(node.value, ast.Constant)
                            and node.value.value == 'break'
                            for node in ast.walk(handler)))

    def test_selected_style_is_high_contrast(self):
        self.assertIn("RESULT_CURSOR_BORDER = '#915100'", SOURCE)
        self.assertIn("RESULT_CURSOR_WIDTH = 2", SOURCE)
        self.assertIn("tree.bind('<FocusOut>', hide_result_cursor)", SOURCE)
        self.assertIn("tree.bind('<<TreeviewSelect>>', schedule_result_cursor)", SOURCE)
        self.assertIn("tree.tag_configure(tags[0], 'background')", SOURCE)
        self.assertIn("background=[('selected', row_background)]", SOURCE)
        self.assertIn("tree.heading('Hits', text='検索ヒット数'", SOURCE)
        self.assertIn("tree.heading('Folder', text='検索フォルダNo.'", SOURCE)

if __name__ == '__main__':
    unittest.main()
