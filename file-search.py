import os
import sys
from pathlib import Path
import tkinter as tk
import tkinter.font
import tkinter.filedialog
import shutil
import datetime

from tkinter import ttk
from tkinter import messagebox
from design_theme import apply_theme, THEME


# 設定ファイルは実行場所ではなく、.py / .exe が置かれたフォルダーから探す。
# PyInstallerでEXE化した場合は、一時展開先ではなくEXEの配置先を使う。
APP_DIR = (Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False)
           else Path(__file__).resolve().parent)
CFG_FILE = APP_DIR / 'file-search.cfg'


THEME_COLORS = THEME["colors"]

# 起動直後の表示初期化では設定を保存しない。
settings_ready = False

searchFolder = ["",""]
saveFolder = ""
sf1_sw = False
sf2_sw = False
num_sw = False
cntNum = 1
infoTxt = ""

# 検索フォルダ番号
sfn0, sfn1, sfnAll = range(3)

name_list = []
name_list_num = []
cur_id = 0

# デスクトップパスを取得
def getDeskTop():
    if os.name == 'nt':
        outFolder = os.path.expanduser(r'~\Desktop')

    elif os.name == 'posix':
        outFolder = os.path.expanduser('~/Desktop')

    return(outFolder)

# 日時付きバックアップフォルダ名を生成
def getSeveFolderTime():
    desktop_dir = getDeskTop()

    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)

    outFolder = desktop_dir + "\\" + str(now.strftime('%Y%m%d_%H%M')) + "_" + "DD_Numbering"

    return(outFolder)

# 数値を3桁のゼロ埋め文字列に変換
def intToStr03(inNum):
    outTxt = '{0:03d}'.format(inNum)
    return(outTxt)

# 指定フォルダ内にファイルがあるか確認
def getFileEx(dir):
    if(len(os.listdir(dir)) != 0):
        return(True)
    else:
        return(False)

#toggleチェック
def sfs1_toggle():
    if sfs1_var.get() == 0:
        sfs1_btn.config(text='OFF', style='ToggleOff.TCheckbutton')
        folderLbl1.configure(style='DisabledFolder.TLabel')

    else:
        sfs1_btn.config(text='ON', style='ToggleOn.TCheckbutton')
        folderLbl1.configure(style='FileSearch.TLabel')

    setListTree()
    if settings_ready:
        persist_current_settings()

#toggleチェック
def sfs2_toggle():
    if sfs2_var.get() == 0:
        sfs2_btn.config(text='OFF', style='ToggleOff.TCheckbutton')
        folderLbl2.configure(style='DisabledFolder.TLabel')
    else:
        sfs2_btn.config(text='ON', style='ToggleOn.TCheckbutton')
        folderLbl2.configure(style='FileSearch.TLabel')

    setListTree()
    if settings_ready:
        persist_current_settings()

# フォルダボタンから直接変更する。変更した値は従来の .cfg に自動保存。
def folderSet(num):
    old_dir = searchFolder[num]
    initial = old_dir if os.path.isdir(old_dir) else str(APP_DIR)
    choice = tk.filedialog.askdirectory(parent=root, initialdir=initial,
                                        title=f'検索フォルダ {num + 1} を選択', mustexist=True)
    if not choice:
        return False

    searchFolder[num] = choice
    if not persist_current_settings():
        searchFolder[num] = old_dir
        return False
    (folderTxt1 if num == sfn0 else folderTxt2).set(choice)
    setListTree()
    return True


def folder1():
    folderSet(sfn0)


def folder2():
    folderSet(sfn1)


def choose_copy_folder():
    """コピー先を直接選択する。キャンセル時は現在の設定を維持。"""
    global saveFolder
    old_dir = saveFolder
    initial = old_dir if os.path.isdir(old_dir) else str(APP_DIR)
    choice = tk.filedialog.askdirectory(parent=root, initialdir=initial,
                                        title='コピー先フォルダを選択', mustexist=True)
    if not choice:
        return False

    saveFolder = choice
    if not persist_current_settings():
        saveFolder = old_dir
        return False
    destination_var.set(choice)
    setInfomation('コピー先フォルダを変更しました。')
    return True

# 有効な検索フォルダからファイル一覧を取得
def getNameList():
    global name_list
    global name_list_num

    name_list = []
    name_list_num = []

    if sfs1_var.get() == 0 and sfs2_var.get() == 0:
        return

    # 有効かつ実在する検索フォルダだけを読み込む。
    # 空文字や無効なパスに対して os.listdir() を呼ばないようにする。
    nl1 = []
    nl1_num = []
    if sfs1_var.get() != 0 and searchFolder[sfn0] != "" and os.path.isdir(searchFolder[sfn0]):
        nl1 = os.listdir(searchFolder[sfn0])
        nl1_num = [sfn0] * len(nl1)

    nl2 = []
    nl2_num = []
    if sfs2_var.get() != 0 and searchFolder[sfn1] != "" and os.path.isdir(searchFolder[sfn1]):
        nl2 = os.listdir(searchFolder[sfn1])
        nl2_num = [sfn1] * len(nl2)

    name_list = nl1 + nl2
    name_list_num = nl1_num + nl2_num

    # ファイル名と検索フォルダ番号の対応を保ったまま降順ソートする。
    zip_sort = sorted(zip(name_list, name_list_num), reverse=True)

    # 対象ファイルが0件なら空のままにする。
    if zip_sort:
        name_list, name_list_num = zip(*zip_sort)
    else:
        name_list, name_list_num = [], []

# 取得したファイル一覧をTreeviewへ表示
def FileListSetTree():

    tree.delete(*tree.get_children())

    # レコードの追加
    for i in range(len(name_list)):
        tree.insert(parent='', index='end', iid=i ,values=(name_list[i], '', "SF" + str(name_list_num[i]+1)))

# Treeviewの内容を更新
def setListTree():
        getNameList()
        FileListSetTree()

# ステータス表示を更新
def setInfomation(setstr):
    infoTxt = setstr
    infomationTxt.set(infoTxt)

# 検索結果の色分け（ヒット数が多いほど背景が濃い）。
# 最高ランクも黒系の文字が読みやすい明るさに抑える。
HIT_COLORS = ('#E7F2FD', '#B6DAF8', '#81BCEA', '#68ABE0')
HIT_FOREGROUND = '#172B42'


def search_hit_color(hit_count, max_hit):
    """検索結果のヒット数を4段階の背景色に変換する。"""
    if hit_count <= 0 or max_hit <= 0:
        return THEME_COLORS['surface']
    level = min(len(HIT_COLORS) - 1,
                (hit_count * len(HIT_COLORS) - 1) // max_hit)
    return HIT_COLORS[level]


def funcWordSet(event):
    global name_list
    global cur_id

    #リストデータ削除
    tree.delete(*tree.get_children())

    #文字列を取得
    getTxt = entry1.get()

    #スペース（全角、半角）を削除
    getTxt = getTxt.replace(' ', '')
    getTxt = getTxt.replace('　', '')

    search_txt = getTxt

    if search_txt == "":
        setListTree()

    #リスト化
    getTxt = []

    #ファイル一覧を取得
    getNameList()

    name_list_hit = [0] * len(name_list)

    cnt_max = 0
    for i,name in enumerate(name_list):
        for ii in range(len(search_txt)):

            if name.find(search_txt[ii]) != -1:
                name_list_hit[i] += 1

                if cnt_max < name_list_hit[i]:
                    cnt_max = name_list_hit[i]

    cur_id = None
    cnt = 0

    cntlp = cnt_max
    while cntlp>0:

        for i in range(len(name_list)):
            if name_list_hit[i] == cntlp:
                tree.insert(parent='', index='end', iid=cnt ,values=(name_list[i],name_list_hit[i],"SF"+str(name_list_num[i]+1)), tags=str(cnt))

                # 並び順はそのまま、背景色を4段階で明確に区別。
                col = search_hit_color(name_list_hit[i], cnt_max)
                tree.tag_configure(str(cnt), background=col, foreground=HIT_FOREGROUND)

                cur_id = 0
                cnt += 1

        cntlp -= 1

# Tabで検索結果の先頭行を選択し、キーボード操作先も一覧へ移動する。
def funcWordSetTab(event):
    if cur_id is not None and tree.exists(cur_id):
        tree.focus(cur_id)               # Enterキーでコピーする対象行
        tree.selection_set(cur_id)       # 選択行の背景・文字色を反映
        tree.see(cur_id)                 # 一覧の表示範囲外ならスクロール
        tree.focus_set()                 # Tab後の↑↓/Enterを一覧で受け付ける
        return 'break'                  # 標準のTab移動で上書きされないようにする

# 検索結果からTabで検索欄へ戻り、すぐ次の検索文字を入力できる。
def funcResultTab(event):
    entry1.focus_set()
    entry1.selection_range(0, tk.END)
    return 'break'


# 選択ファイルをコピー。検索とファイル名の連番付与形式は従来どおり。
def select_record(event):
    global cntNum

    record_id = tree.focus()
    if not record_id or not tree.exists(record_id):
        setInfomation('コピーするファイルを選択してください。')
        return 'break'
    values = tree.item(record_id, 'values')
    if len(values) < 3:
        return 'break'
    if not saveFolder or not os.path.isdir(saveFolder):
        setInfomation('コピー先フォルダを指定してください。')
        return 'break'

    sf_num = sfn0 if values[2] == 'SF1' else sfn1
    source_file = Path(searchFolder[sf_num]) / values[0]
    numbering = bool(nmb_var.get())
    target_name = (f'{cntNum:03d}_' if numbering else '') + values[0]
    target_file = Path(saveFolder) / target_name

    # 同じ場所へのコピーと、意図しない上書きを防ぐ。
    # 「いいえ」を既定にし、既存ファイルは明示的に承認された場合だけ上書きする。
    if source_file.resolve() == target_file.resolve():
        setInfomation('コピー元とコピー先が同じファイルです。')
        return 'break'
    if target_file.is_dir():
        setInfomation('コピー先に同名のフォルダがあります。')
        return 'break'
    if target_file.exists() and not messagebox.askyesno(
            '上書きの確認',
            f'コピー先に同じ名前のファイルが存在します。\n\n'
            f'{target_name}\n\n上書きしますか？',
            icon='warning', default=messagebox.NO, parent=root):
        setInfomation('コピーを中止しました（同名ファイル）。')
        return 'break'

    try:
        shutil.copy2(source_file, target_file)
    except OSError as exc:
        setInfomation(f'コピー失敗: {type(exc).__name__}: {exc}')
        return 'break'

    # 実際にコピーできた場合のみ連番を進める。
    if numbering:
        cntNum += 1
        numberTxt.set(intToStr03(cntNum))
        persist_current_settings()
    setInfomation('-> ' + target_name)
    entry1.focus_set()
    entry1.selection_range(0, tk.END)
    return 'break'


def funcNumberGet(event=None):
    """メイン画面の次の番号を更新。3桁以上も入力可能。"""
    global cntNum
    value = entry2.get().strip()
    if (not value or not value.isascii() or not value.isdecimal()
            or len(value) > 12):
        messagebox.showerror('番号エラー', '番号は12桁以内の半角数字で入力してください。',
                             parent=root)
        numberTxt.set(intToStr03(cntNum))
        return 'break'
    old_number = cntNum
    cntNum = int(value)
    if not persist_current_settings():
        cntNum = old_number
    numberTxt.set(intToStr03(cntNum))
    if event is not None and getattr(event, 'keysym', None) == 'Return':
        entry1.focus_set()
    return 'break'


def nmb_toggle():
    nmb_btn.configure(text=('ON' if nmb_var.get() else 'OFF'),
                      style=('ToggleOn.TCheckbutton' if nmb_var.get()
                             else 'ToggleOff.TCheckbutton'))
    if settings_ready:
        persist_current_settings()

# 設定ファイルを読み込む
def getCfgFile():
    global searchFolder
    global saveFolder
    global sf1_sw
    global sf2_sw
    global num_sw
    global cntNum

    if CFG_FILE.is_file():
        with CFG_FILE.open('r', encoding='utf-8') as f:

            # ','と'\n'を取り除いて、2次元配列に格納する
            lines = f.readlines()
            datas = []
            for line in lines:
                row = line.strip().split(';')
                row = [col.replace('\n', '') for col in row]
                datas.append(row)

            for data in datas:
                match data[0]:
                    case 'in1':
                        searchFolder[sfn0] = data[1]

                    case 'in2':
                        searchFolder[sfn1] = data[1]

                    case 'out':
                        saveFolder = data[1]

                    case 'sf1_sw':
                        sf1_sw = data[1]

                    case 'sf2_sw':
                        sf2_sw = data[1]

                    case 'num_sw':
                        num_sw = data[1]

                    case 'cntNum':
                        cntNum = int(data[1])

            # 存在チェック
            if saveFolder and not os.path.exists(saveFolder):
                os.makedirs(saveFolder, exist_ok=True)



# ---------------------------------------------------------------------------
# 設定ファイルの保存処理（メイン画面の変更を自動保存）
# ---------------------------------------------------------------------------
def save_cfg_values(values: dict[str, str]) -> None:
    """既存の独自 .cfg 形式を維持し、7項目だけを書き換える。

    未知の項目やコメントは残す。保存途中でファイルが壊れないよう、
    一時ファイルを作ってから置換する。初回は元ファイルのバックアップも残す。
    """
    # セミコロンは既存の設定形式で区切り文字として使われている。
    # 改行を含む文字列も設定データへ混入させない。
    for key, value in values.items():
        if any(mark in value for mark in (';', '\r', '\n')):
            raise ValueError(f'「{key}」に使用できない文字が含まれています。')

    lines = CFG_FILE.read_text(encoding='utf-8').splitlines() if CFG_FILE.exists() else []
    seen: set[str] = set()
    updated: list[str] = []
    for line in lines:
        key = line.split(';', 1)[0]
        if key in values:
            # 重複定義を除き、同じ設定が何度も読み込まれないようにする。
            if key not in seen:
                updated.append(f'{key};{values[key]}')
                seen.add(key)
        else:
            updated.append(line)
    for key, value in values.items():
        if key not in seen:
            updated.append(f'{key};{value}')

    backup = CFG_FILE.with_suffix('.cfg.bak')
    temporary = CFG_FILE.with_suffix('.cfg.tmp')
    try:
        # 変更前の設定ファイルを初回保存時のみ退避する。
        if CFG_FILE.is_file() and not backup.exists():
            shutil.copy2(CFG_FILE, backup)
        with temporary.open('w', encoding='utf-8', newline='') as stream:
            stream.write('\n'.join(updated) + '\n')
        temporary.replace(CFG_FILE)
    finally:
        if temporary.exists():
            temporary.unlink()


def persist_current_settings():
    """現在のメイン画面の設定を既存の .cfg 形式へ保存する。"""
    values = {
        'in1': searchFolder[sfn0],
        'in2': searchFolder[sfn1],
        'out': saveFolder,
        'sf1_sw': str(int(sfs1_var.get())),
        'sf2_sw': str(int(sfs2_var.get())),
        'num_sw': str(int(nmb_var.get())),
        'cntNum': intToStr03(cntNum),
    }
    try:
        save_cfg_values(values)
    except (OSError, ValueError) as exc:
        messagebox.showerror('設定保存エラー', str(exc), parent=root)
        return False
    return True


# main ----------------------------------------------------------------------
# 従来どおり、ウィジェット生成前に設定を読み込む。
getCfgFile()
# テーマ適用はGUIの構築時に一度だけ行う。検索・コピー等の処理は従来の関数を使う。
root = tk.Tk()
root.title('File-Search v1.00  |  Urban Theme')
root.geometry('1060x840')
root.minsize(790, 630)
root.configure(bg=THEME_COLORS['background'])
style = apply_theme(root)

# タイトル、検索欄、コピー先等はすべて標準Tkinter / ttk部品で構成。
font_family = THEME['options'].get('font_family', 'Yu Gothic UI')
font_size = int(THEME['options'].get('font_size', 10))
font = tk.font.Font(root, family=font_family, size=font_size)
font_bold = tk.font.Font(root, family=font_family, size=font_size, weight='bold')
font_search_word = tk.font.Font(root, family=font_family, size=font_size + 2)

# Treeviewはファイル名・ヒット数・検索フォルダNo.を見出し付きで表示する。
# 列を入れ替えたため、コピー元フォルダの判定にも3列目を使う。
style.configure('FileSearch.Treeview', rowheight=30, background=THEME_COLORS['surface'],
                fieldbackground=THEME_COLORS['surface'], foreground=THEME_COLORS['text'],
                font=(font_family, font_size + 1), borderwidth=0)
# 検索ヒット数の青系背景と混同しないよう、選択行はアンバー＋濃色文字。
# ttkのselected状態を用いるため、選択解除後は各行のヒット数色へ戻る。
SELECTED_ROW_BG = '#FFD38A'
SELECTED_ROW_FG = '#172B42'
style.map('FileSearch.Treeview', background=[('selected', SELECTED_ROW_BG)],
          foreground=[('selected', SELECTED_ROW_FG)])
style.configure('FileSearch.Treeview.Heading',
                background=THEME_COLORS['surface_alt'],
                foreground=THEME_COLORS['text'],
                font=(font_family, font_size, 'bold'),
                padding=(7, 7))
style.map('FileSearch.Treeview.Heading', background=[('active', THEME_COLORS['selection'])])
style.configure('FileSearch.TFrame', background=THEME_COLORS['surface'])
style.configure('FileSearch.TLabel', background=THEME_COLORS['surface'],
                foreground=THEME_COLORS['text'], font=(font_family,font_size))
style.configure('FileSearchMuted.TLabel', background=THEME_COLORS['surface'],
                foreground=THEME_COLORS['muted'], font=(font_family,font_size))
style.configure('FileSearchTitle.TLabel', background=THEME_COLORS['background'],
                foreground=THEME_COLORS['text'], font=(font_family,20,'bold'))
style.configure('FileSearchHeader.TLabel', background=THEME_COLORS['surface_alt'],
                foreground=THEME_COLORS['accent'], font=(font_family,font_size+1,'bold'))
style.configure('DisabledFolder.TLabel', background=THEME_COLORS['surface_alt'],
                foreground=THEME_COLORS['muted'], font=(font_family,font_size))
style.configure('ToggleOn.TCheckbutton', background=THEME_COLORS['surface'],
                foreground=THEME_COLORS['accent'], font=(font_family,font_size,'bold'))
style.configure('ToggleOff.TCheckbutton', background=THEME_COLORS['surface'],
                foreground=THEME_COLORS['muted'], font=(font_family,font_size,'bold'))


# 使用する設定はすべてメイン画面から操作できるため、設定画面は設けない。
outer = ttk.Frame(root, padding=(20, 16, 20, 16), style='App.TFrame')
outer.pack(fill='both', expand=True)
outer.columnconfigure(0, weight=1)
outer.rowconfigure(3, weight=1)

header = ttk.Frame(outer, style='App.TFrame')
header.grid(row=0, column=0, sticky='ew', pady=(0, 16))
header.columnconfigure(0, weight=1)
title_area = ttk.Frame(header, style='App.TFrame')
title_area.grid(row=0, column=0, sticky='w')
ttk.Label(title_area, text='File-Search', style='FileSearchTitle.TLabel').pack(anchor='w')
ttk.Label(title_area, text='2つのフォルダを検索し、選択したファイルをコピー',
          style='Muted.TLabel').pack(anchor='w', pady=(4, 0))

# 上段: 入力フォルダと出力フォルダ。
folders_card = ttk.Frame(outer, padding=12, style='Card.TFrame')
folders_card.grid(row=1, column=0, sticky='ew', pady=(0, 12))
folders_card.columnconfigure(2, weight=1)
ttk.Label(folders_card, text='検索するフォルダ', style='Section.TLabel').grid(
    row=0, column=0, columnspan=3, sticky='w', pady=(0, 8))

# ON/OFFは標準ttk.Checkbuttonを使用し、既存の切替処理を呼ぶ。
def themed_check(parent, variable, command):
    return ttk.Checkbutton(parent, text='ON', variable=variable, onvalue=1, offvalue=0,
                           command=command, style='ToggleOn.TCheckbutton', takefocus=0)

sfs1_var = tk.IntVar(value=sf1_sw)
sfs1_btn = themed_check(folders_card, sfs1_var, sfs1_toggle)
sfs1_btn.grid(row=1, column=0, padx=(0, 10), pady=5, sticky='w')
sfolder1 = ttk.Button(folders_card, text='検索フォルダ 1', command=folder1,
                       style='Secondary.TButton')
sfolder1.grid(row=1, column=1, pady=5, sticky='w')
folderTxt1 = tk.StringVar(value=searchFolder[sfn0])
folderLbl1 = ttk.Label(folders_card, textvariable=folderTxt1,
                       style='FileSearch.TLabel', anchor='w', padding=(12, 0))
folderLbl1.grid(row=1, column=2, sticky='ew', pady=5)

sfs2_var = tk.IntVar(value=sf2_sw)
sfs2_btn = themed_check(folders_card, sfs2_var, sfs2_toggle)
sfs2_btn.grid(row=2, column=0, padx=(0, 10), pady=5, sticky='w')
sfolder2 = ttk.Button(folders_card, text='検索フォルダ 2', command=folder2,
                       style='Secondary.TButton')
sfolder2.grid(row=2, column=1, pady=5, sticky='w')
folderTxt2 = tk.StringVar(value=searchFolder[sfn1])
folderLbl2 = ttk.Label(folders_card, textvariable=folderTxt2,
                       style='FileSearch.TLabel', anchor='w', padding=(12, 0))
folderLbl2.grid(row=2, column=2, sticky='ew', pady=5)

ttk.Separator(folders_card).grid(row=3, column=0, columnspan=3,
                                sticky='ew', pady=(10, 8))
ttk.Button(folders_card, text='コピー先フォルダ',
           command=choose_copy_folder, style='Secondary.TButton').grid(
               row=4, column=1, sticky='w', pady=5)
destination_var = tk.StringVar(value=saveFolder)
copy_destination = ttk.Label(folders_card, textvariable=destination_var,
                              style='FileSearch.TLabel', anchor='w', padding=(12, 0))
copy_destination.grid(row=4, column=2, sticky='ew', pady=5)

# 検索入力と結果一覧。
search_card = ttk.Frame(outer, padding=(12, 12, 12, 12), style='Card.TFrame')
search_card.grid(row=2, column=0, sticky='ew', pady=(0, 12))
search_card.columnconfigure(1, weight=1)
ttk.Label(search_card, text='ファイルを検索', style='Section.TLabel').grid(
    row=0, column=0, columnspan=2, sticky='w', pady=(0, 8))
ttk.Label(search_card, text='検索文字', style='FileSearch.TLabel').grid(
    row=1, column=0, sticky='w', padx=(0, 12))
entry1 = ttk.Entry(search_card, font=font_search_word)
entry1.grid(row=1, column=1, sticky='ew')
entry1.bind('<Return>', funcWordSet)
entry1.bind('<Tab>', funcWordSetTab)
ttk.Label(search_card, text='Enter: 検索  /  Tab: 検索結果へ  /  結果上でTab: 検索欄へ  /  Enter: コピー',
          style='FileSearchMuted.TLabel').grid(row=2, column=0, columnspan=2,
                                                sticky='w', pady=(8, 0))

list_card = ttk.Frame(outer, padding=12, style='Card.TFrame')
list_card.grid(row=3, column=0, sticky='nsew', pady=(0, 12))
list_card.columnconfigure(0, weight=1)
list_card.rowconfigure(2, weight=1)
ttk.Label(list_card, text='検索結果', style='Section.TLabel').grid(
    row=0, column=0, sticky='w', pady=(0, 5))
# 文字ごとに一致判定。SF1/SF2はそれぞれ検索フォルダ1/2を表す。
ttk.Label(
    list_card,
    text='SF1＝検索フォルダ1  /  SF2＝検索フォルダ2  /  青が濃いほどヒット数が多い  /  選択中はオレンジ',
    style='FileSearchMuted.TLabel'
).grid(row=1, column=0, sticky='w', pady=(0, 7))
# 標準ヘッダーで見出しと各列を正確に揃える（列幅の変更にも追従）。
column = ('Name', 'Hits', 'Folder')
tree = ttk.Treeview(list_card, columns=column, selectmode='browse',
                    show='headings', style='FileSearch.Treeview')
tree.grid(row=2, column=0, sticky='nsew')
tree.column('Name', anchor='w', width=450, stretch=True)
tree.column('Hits', anchor='center', width=130, minwidth=110, stretch=False)
tree.column('Folder', anchor='center', width=165, minwidth=150, stretch=False)
tree.heading('Name', text='ファイル名', anchor='w')
tree.heading('Hits', text='検索ヒット数', anchor='center')
tree.heading('Folder', text='検索フォルダNo.', anchor='center')
tree.bind('<Return>', select_record)
tree.bind('<Tab>', funcResultTab)
tree.bind('<Shift-Tab>', funcResultTab)
scr_bar = ttk.Scrollbar(list_card, orient='vertical', command=tree.yview)
scr_bar.grid(row=2, column=1, sticky='ns')
tree.configure(yscrollcommand=scr_bar.set)

# 連番のON/OFFと次の番号もメイン画面で変更・保存できる。
bottom = ttk.Frame(outer, padding=12, style='Card.TFrame')
bottom.grid(row=4, column=0, sticky='ew')
bottom.columnconfigure(4, weight=1)
nmb_var = tk.IntVar(value=num_sw)
nmb_btn = themed_check(bottom, nmb_var, nmb_toggle)
nmb_btn.grid(row=0, column=0, sticky='w', padx=(0, 8))
ttk.Label(bottom, text='連番付与', style='FileSearch.TLabel').grid(
    row=0, column=1, sticky='w', padx=(0, 14))
numberTxt = tk.StringVar(value=intToStr03(cntNum))
ttk.Label(bottom, text='次の番号', style='FileSearch.TLabel').grid(
    row=0, column=2, sticky='w', padx=(0, 7))
entry2 = ttk.Entry(bottom, textvariable=numberTxt, font=font, width=9)
entry2.grid(row=0, column=3, sticky='w')
entry2.bind('<Return>', funcNumberGet)
entry2.bind('<FocusOut>', funcNumberGet)
infomationTxt = tk.StringVar(value=infoTxt)
infomationLbl = ttk.Label(bottom, textvariable=infomationTxt, style='FileSearchMuted.TLabel')
infomationLbl.grid(row=0, column=4, sticky='e', padx=(20,0))

sfs1_toggle()
sfs2_toggle()
nmb_toggle()
setListTree()
settings_ready = True
entry1.focus_set()
root.mainloop()
