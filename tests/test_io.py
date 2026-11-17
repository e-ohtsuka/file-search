"""一時データとイベントループの代替を使う、表示環境に依存しないテスト。"""
import ast
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch

APP = Path(__file__).resolve().parents[1]


class Loop:
    def __init__(self):
        self.callbacks = []

    def after(self, delay, callback):
        self.callbacks.append(callback)

    def drain(self):
        deadline = time.monotonic() + 5
        while self.callbacks:
            if time.monotonic() > deadline:
                raise AssertionError('task timed out')
            self.callbacks.pop(0)()
            time.sleep(.001)


class IOTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        # 起動部分を実行せず、実際の関数定義と初期値を読み込む。
        syntax = ast.parse((APP / 'file-search.py').read_text(encoding='utf-8'))
        nodes = []
        for node in syntax.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'getCfgFile':
                break
            nodes.append(node)
        self.ns = {'__file__': str(self.path / 'file-search.py')}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), 'file-search.py', 'exec'), self.ns)
        self.ns['root'] = Loop()
        self.ns['infomationTxt'] = Mock()

    def config(self, content):
        (self.path / 'file-search.cfg').write_text(content, encoding='utf-8')
        self.ns['getCfgFile']()

    def test_config_invalid_fields_keep_valid_values(self):
        self.config('in1\ncntNum;abc\nsf1_sw;bad\nsf2_sw;1\nin2;dummy\ncustom;keep\n')
        self.assertEqual(self.ns['cntNum'], 1)
        self.assertFalse(self.ns['sf1_sw'])
        self.assertEqual(self.ns['sf2_sw'], 1)
        self.assertEqual(self.ns['searchFolder'], ['', 'dummy'])
        self.assertIn('cntNum', self.ns['infoTxt'])

    def test_config_encoding_and_read_errors(self):
        (self.path / 'file-search.cfg').write_bytes(b'\xff')
        self.ns['getCfgFile']()
        self.assertIn('設定読込失敗', self.ns['infoTxt'])
        with patch.object(Path, 'read_text', side_effect=PermissionError('denied')):
            self.ns['getCfgFile']()
        self.assertIn('denied', self.ns['infoTxt'])

    def test_config_destination_creation_failure(self):
        with patch('os.makedirs', side_effect=PermissionError('denied')):
            self.config('out;' + str(self.path / 'output'))
        self.assertIn('コピー先の準備失敗', self.ns['infoTxt'])

    def test_legacy_config_and_unknown_keys_survive_save(self):
        self.config('cntNum;007\nsf1_sw;1\ncustom;keep\n# comment\n')
        self.assertEqual(self.ns['cntNum'], 7)
        self.ns['save_cfg_values']({'cntNum': '008'})
        stored = (self.path / 'file-search.cfg').read_text(encoding='utf-8')
        self.assertIn('custom;keep', stored)
        self.assertIn('# comment', stored)
        self.assertTrue((self.path / 'file-search.cfg.bak').is_file())

    def test_only_files_and_original_character_scoring(self):
        (self.path / 'ab.txt').write_text('dummy')
        (self.path / 'a.txt').write_text('dummy')
        (self.path / 'ab-folder').mkdir()
        rows, errors = self.ns['collect_files']((str(self.path), ''), (1, 0), 'aab')
        self.assertEqual(rows, [('ab.txt', 3, 0), ('a.txt', 2, 0)])
        self.assertFalse(errors)

    def test_permission_and_missing_folder_are_reported(self):
        with patch('os.scandir', side_effect=PermissionError('denied')):
            rows, errors = self.ns['collect_files']((str(self.path),), (1,), '')
        self.assertEqual(rows, [])
        self.assertIn('denied', errors[0])
        rows, errors = self.ns['collect_files']((str(self.path / 'missing'),), (1,), '')
        self.assertTrue(errors)

    def test_background_keeps_loop_available_and_callback_on_main_thread(self):
        release = threading.Event()
        self.addCleanup(release.set)
        callback = Mock()
        self.ns['run_background'](lambda: release.wait(3), callback)
        self.ns['root'].callbacks.pop(0)()
        callback.assert_not_called()
        release.set()
        self.ns['root'].drain()
        callback.assert_called_once_with(True, None)

    def prepare_copy(self):
        source = self.path / 'source'
        dest = self.path / 'dest'
        source.mkdir()
        dest.mkdir()
        (source / 'dummy.txt').write_text('dummy')
        self.ns.update(searchFolder=[str(source), ''], saveFolder=str(dest), cur_id=0,
                       tree=Mock(), nmb_var=Mock(), entry1=Mock(),
                       numberTxt=Mock(), persist_current_settings=Mock())
        self.ns['tree'].focus.return_value = '0'
        self.ns['tree'].item.return_value = ('dummy.txt', 1, 'SF1')
        self.ns['nmb_var'].get.return_value = 1
        return source, dest

    def test_copy_success_and_duplicate_enter(self):
        source, dest = self.prepare_copy()
        self.ns['select_record'](None)
        self.ns['select_record'](None)
        self.ns['root'].drain()
        self.assertEqual((dest / '001_dummy.txt').read_text(), 'dummy')
        self.assertEqual(self.ns['cntNum'], 2)

    def test_copy_failure_and_source_becomes_directory(self):
        source, dest = self.prepare_copy()
        with patch('shutil.copy2', side_effect=PermissionError('denied')):
            self.ns['select_record'](None)
            self.ns['root'].drain()
        self.assertEqual(self.ns['cntNum'], 1)
        self.assertFalse(self.ns['copy_busy'])
        (source / 'dummy.txt').unlink()
        (source / 'dummy.txt').mkdir()
        self.ns['select_record'](None)
        self.ns['root'].drain()
        self.assertFalse((dest / '001_dummy.txt').exists())

    def test_copy_path_resolution_failure_and_close_wait(self):
        self.prepare_copy()
        with patch.object(Path, 'resolve', side_effect=OSError('resolve failed')):
            self.ns['select_record'](None)
            self.ns['root'].drain()
        self.assertFalse(self.ns['copy_busy'])
        self.assertEqual(self.ns['cntNum'], 1)
        loop = self.ns['root']
        loop.destroy = Mock()
        self.ns['copy_busy'] = True
        self.ns['close_app']()
        loop.destroy.assert_not_called()
        self.ns['copy_busy'] = False
        loop.drain()
        loop.destroy.assert_called_once()

    def test_stale_search_and_chunked_render(self):
        ns = self.ns
        ns.update(tree=Mock(), sfs1_var=Mock(), sfs2_var=Mock(), schedule_result_cursor=Mock())
        ns['tree'].get_children.return_value = ()
        callbacks = []
        ns['run_background'] = lambda work, done: callbacks.append(done)
        ns['setListTree']('old')
        ns['setListTree']('new')
        callbacks[0](([('old', 1, 0)], []), None)
        ns['tree'].insert.assert_not_called()
        callbacks[1](([(f'file{i}', 1, 0) for i in range(1000)], []), None)
        self.assertEqual(ns['tree'].insert.call_count, 200)
        ns['root'].drain()
        self.assertEqual(ns['tree'].insert.call_count, 1000)


if __name__ == '__main__':
    unittest.main()
