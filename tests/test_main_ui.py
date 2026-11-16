"""Main GUI behaviors. Run with `xvfb-run -a python -m unittest discover -s tests -v` on Linux."""
from pathlib import Path
import os
import runpy
import shutil
import sys
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

APP = Path(__file__).resolve().parents[1]


@unittest.skipIf(os.name != 'nt' and not os.environ.get('DISPLAY'),
                 'Tk GUI tests require an active display')
class UITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        for name in ('file-search.py', 'design_theme.py', 'design_theme.json'):
            shutil.copy2(APP / name, self.path / name)
        self.source = self.path / 'source'
        self.destination = self.path / 'destination'
        self.source.mkdir()
        self.destination.mkdir()
        (self.source / '20250901-我妻功.txt').write_text('dummy', encoding='utf-8')
        sys.path.insert(0, str(self.path))
        self.addCleanup(lambda: sys.path.remove(str(self.path)))
        with patch.object(tk.Tk, 'mainloop', lambda root: None):
            namespace = runpy.run_path(str(self.path / 'file-search.py'))
        self.ns = namespace['folderSet'].__globals__
        self.root = self.ns['root']
        self.addCleanup(self.root.destroy)
        self.root.update()
        self.root.focus_force()
        self.root.update()

    def setup_folder(self):
        with patch('tkinter.filedialog.askdirectory', return_value=str(self.source)):
            self.assertTrue(self.ns['folderSet'](0))
        with patch('tkinter.filedialog.askdirectory', return_value=str(self.destination)):
            self.assertTrue(self.ns['choose_copy_folder']())
        self.ns['sfs1_var'].set(1)
        self.ns['sfs1_toggle']()

    def test_startup_does_not_write_config_and_has_destination_button(self):
        self.assertFalse((self.path / 'file-search.cfg').exists())
        self.assertEqual(self.ns['destination_var'].get(), '')
        self.assertFalse(hasattr(self.ns, 'open_settings_dialog'))

    def test_folder_destination_and_switch_auto_save(self):
        self.setup_folder()
        stored = (self.path / 'file-search.cfg').read_text(encoding='utf-8')
        self.assertIn('in1;' + str(self.source), stored)
        self.assertIn('out;' + str(self.destination), stored)
        self.assertIn('sf1_sw;1', stored)
        self.assertEqual(self.ns['destination_var'].get(), str(self.destination))

    def test_tab_moves_back_and_forth_and_marks_selected_row(self):
        self.setup_folder()
        entry = self.ns['entry1']
        entry.insert(0, '我妻功')
        self.ns['funcWordSet'](None)
        entry.focus_force()
        self.root.update()
        entry.event_generate('<Tab>', when='tail')
        self.root.update()
        self.assertEqual(self.root.focus_get(), self.ns['tree'])
        self.assertTrue(self.ns['tree'].selection())
        self.ns['tree'].event_generate('<Tab>', when='tail')
        self.root.update()
        self.assertEqual(self.root.focus_get(), entry)
        self.assertEqual(entry.selection_range(0, tk.END), None)

    def test_next_number_copy_and_persist(self):
        self.setup_folder()
        self.ns['nmb_var'].set(1)
        self.ns['nmb_toggle']()
        number = self.ns['entry2']
        number.delete(0, 'end')
        number.insert(0, '007')
        self.ns['funcNumberGet']()
        self.assertEqual(self.ns['cntNum'], 7)
        self.ns['entry1'].insert(0, '我妻功')
        self.ns['funcWordSet'](None)
        self.ns['funcWordSetTab'](None)
        self.ns['select_record'](None)
        self.assertTrue((self.destination / '007_20250901-我妻功.txt').is_file())
        self.assertIn('cntNum;008', (self.path / 'file-search.cfg').read_text(encoding='utf-8'))

    def prepare_copy(self, number=7):
        """既存の検索・コピー手順をUIから準備する。"""
        self.setup_folder()
        self.ns['nmb_var'].set(1)
        self.ns['nmb_toggle']()
        self.ns['entry2'].delete(0, 'end')
        self.ns['entry2'].insert(0, f'{number:03d}')
        self.ns['funcNumberGet']()
        self.ns['entry1'].insert(0, '我妻功')
        self.ns['funcWordSet'](None)
        self.ns['funcWordSetTab'](None)

    def test_new_file_does_not_ask_for_overwrite(self):
        self.prepare_copy()
        with patch('tkinter.messagebox.askyesno') as ask:
            self.ns['select_record'](None)
        ask.assert_not_called()
        self.assertEqual(self.ns['cntNum'], 8)
        self.assertEqual((self.destination / '007_20250901-我妻功.txt').read_text(encoding='utf-8'), 'dummy')

    def test_existing_file_cancel_keeps_content_and_number(self):
        self.prepare_copy()
        target = self.destination / '007_20250901-我妻功.txt'
        target.write_text('KEEP', encoding='utf-8')
        with patch('tkinter.messagebox.askyesno', return_value=False) as ask:
            self.ns['select_record'](None)
        self.assertEqual(target.read_text(encoding='utf-8'), 'KEEP')
        self.assertEqual(self.ns['cntNum'], 7)
        self.assertIn('cntNum;007', (self.path / 'file-search.cfg').read_text(encoding='utf-8'))
        self.assertIn('コピーを中止', self.ns['infomationTxt'].get())
        self.assertEqual(ask.call_args.kwargs['default'], tk.messagebox.NO)

    def test_existing_file_confirm_overwrites_and_increments_once(self):
        self.prepare_copy()
        target = self.destination / '007_20250901-我妻功.txt'
        target.write_text('OLD', encoding='utf-8')
        with patch('tkinter.messagebox.askyesno', return_value=True) as ask:
            self.ns['select_record'](None)
        ask.assert_called_once()
        self.assertEqual(target.read_text(encoding='utf-8'), 'dummy')
        self.assertEqual(self.ns['cntNum'], 8)
        self.assertIn('cntNum;008', (self.path / 'file-search.cfg').read_text(encoding='utf-8'))

    def test_copy_failure_does_not_increment(self):
        self.prepare_copy()
        with patch('shutil.copy2', side_effect=PermissionError('locked')):
            self.ns['select_record'](None)
        self.assertEqual(self.ns['cntNum'], 7)
        self.assertIn('コピー失敗', self.ns['infomationTxt'].get())

    def test_copy_source_same_as_destination_is_rejected(self):
        self.setup_folder()
        with patch('tkinter.filedialog.askdirectory', return_value=str(self.source)):
            self.ns['choose_copy_folder']()
        self.ns['entry1'].insert(0, '我妻功')
        self.ns['funcWordSet'](None)
        self.ns['funcWordSetTab'](None)
        with patch('shutil.copy2') as copy_action:
            self.ns['select_record'](None)
        copy_action.assert_not_called()
        self.assertIn('同じファイル', self.ns['infomationTxt'].get())

    def test_existing_directory_is_not_copy_destination(self):
        self.prepare_copy()
        target = self.destination / '007_20250901-我妻功.txt'
        target.mkdir()
        with patch('shutil.copy2') as copy_action:
            self.ns['select_record'](None)
        copy_action.assert_not_called()
        self.assertEqual(self.ns['cntNum'], 7)

    def test_cancel_destination_keeps_previous(self):
        self.setup_folder()
        with patch('tkinter.filedialog.askdirectory', return_value=''):
            self.assertFalse(self.ns['choose_copy_folder']())
        self.assertEqual(self.ns['saveFolder'], str(self.destination))

    def test_existing_cfg_unknown_keys_are_preserved(self):
        self.setup_folder()
        file = self.path / 'file-search.cfg'
        file.write_text(file.read_text(encoding='utf-8') + 'custom;keep-me\n', encoding='utf-8')
        self.ns['nmb_var'].set(1)
        self.ns['nmb_toggle']()
        self.assertIn('custom;keep-me', file.read_text(encoding='utf-8'))
        self.assertTrue((self.path / 'file-search.cfg.bak').is_file())


if __name__ == '__main__':
    unittest.main()
