# GUI Design Studio v0.9.2 から出力した Urban テーマ。
# 標準ttk限定: Canvas製カスタム部品や外部GUIライブラリは使用しません。
THEME = {'schema_version': 1, 'id': 'urban', 'name': 'Urban', 'description': '都市的なブルーグレー。業務ツールに', 'origin': 'exported', 'palette_family': 'ブルー', 'render_mode': 'standard_ttk', 'requires_custom': False, 'colors': {'background': '#F0F5FB', 'surface': '#FFFFFF', 'surface_alt': '#E6EFFB', 'accent': '#246BC4', 'accent_hover': '#1453A1', 'accent_text': '#FFFFFF', 'text': '#253A53', 'muted': '#61758E', 'border': '#BED0E5', 'field_background': '#FFFFFF', 'selection': '#D4E5FF', 'success': '#36835F', 'warning': '#B88332', 'danger': '#BE5057'}, 'options': {'density': 'compact', 'button_style': 'outline', 'button_shape': 'standard', 'slider_shape': 'standard', 'corner_radius': 10, 'frame_border': 1, 'group_padding': 10, 'panel_padding': 14, 'control_gap': 9, 'section_gap': 15, 'button_padding_x': 14, 'button_padding_y': 8, 'button_border': 1, 'input_padding_x': 8, 'input_padding_y': 6, 'input_border': 1, 'choice_label_color': 'text', 'choice_font_weight': 'normal', 'choice_indicator_color': 'default', 'choice_indicator_shape': 'check', 'choice_padding_x': 3, 'choice_padding_y': 4, 'choice_font_size': 10, 'font_family': 'Yu Gothic UI', 'font_size': 10, 'font_weight': 'normal', 'title_weight': 'bold', 'section_weight': 'bold', 'title_size': 17, 'section_size': 11, 'row_height': 27, 'tree_heading_weight': 'bold', 'tree_selection_text_role': 'text', 'slider_thumb_size': 16, 'scrollbar_width': 14, 'progress_height': 13, 'progress_color_role': 'accent', 'slider_track_color_role': 'surface_alt', 'input_focus_role': 'accent', 'tab_padding_x': 13, 'tab_padding_y': 7, 'tab_selected_text_role': 'accent', 'frame_relief': 'solid', 'frame_color_role': 'border', 'label_padding_x': 0, 'label_padding_y': 0, 'button_hover_role': 'accent_hover', 'button_pressed_role': 'accent_hover', 'button_disabled_role': 'border', 'button_text_weight': 'normal', 'button_width_chars': 12, 'input_text_weight': 'normal', 'input_selection_role': 'selection', 'input_disabled_bg_role': 'surface_alt', 'input_readonly_bg_role': 'field_background', 'input_arrow_size': 13, 'choice_indicator_size': 16, 'choice_active_bg_role': 'surface', 'choice_disabled_color_role': 'muted', 'slider_thumb_color_role': 'surface', 'slider_trough_border': 1, 'slider_active_role': 'accent', 'scrollbar_appearance': 'flat', 'scrollbar_thumb_role': 'border', 'scrollbar_trough_role': 'background', 'scrollbar_active_role': 'selection', 'scrollbar_arrow_role': 'text', 'scrollbar_border': 1, 'scrollbar_relief': 'flat', 'progress_trough_role': 'surface_alt', 'progress_border': 1, 'muted_font_size': 10, 'status_font_size': 10, 'title_color_role': 'text', 'section_color_role': 'text', 'tree_border': 1, 'tree_heading_padding_x': 7, 'tree_heading_padding_y': 5, 'tree_selected_bg_role': 'selection', 'tab_active_role': 'selection', 'tab_selected_bg_role': 'surface', 'tab_weight': 'normal', 'notebook_border': 1}, 'shape_preset_id': 'shape-outline', 'color_preset_id': 'urban'}

"""GUI Design Studio で使うテーマ適用ランタイム（Python標準ライブラリのみ）。

スタイルを適用するアプリは ttk ウィジェットに style="Primary.TButton" 等を指定できます。
標準ttk限定モードでは Canvas ベースの部品は生成しません。
"""
import tkinter as tk
import hashlib
import copy
from tkinter import ttk


def resolve_theme(theme=None):
    if theme is not None:
        return theme
    return globals().get('THEME', {})


def _get(theme, key, default):
    return theme.get(key, default)


def _install_check_indicator(root, style, style_name, shape, foreground,
                             background, border, size=16):
    """Set a small tick or X through a ttk image element (not a Canvas widget)."""
    holder = root._root()
    cache = getattr(holder, '_gui_studio_indicator_cache', None)
    if cache is None:
        cache = {}
        holder._gui_studio_indicator_cache = cache
    size = max(12, min(24, int(size)))
    key = (shape, foreground, background, border, size)
    if key not in cache:
        digest = hashlib.sha256(repr(key).encode('utf-8')).hexdigest()[:14]
        element = 'GDSCheck' + digest + '.indicator'
        images = []
        for selected in (False, True):
            im = tk.PhotoImage(master=holder, width=size, height=size)
            im.put(background, to=(0, 0, size, size))
            im.put(border, to=(1, 1, size-1, size-1))
            im.put(background, to=(2, 2, size-2, size-2))
            if selected:
                pixels = set()
                if shape == 'cross':
                    for i in range(4, 12):
                        for d in (-1, 0, 1):
                            pixels.update(((i, i+d), (15-i, i+d)))
                else:
                    for i in range(3, 8):
                        for d in (-1, 0, 1):
                            pixels.add((i, i+3+d))
                    for i in range(7, 13):
                        for d in (-1, 0, 1):
                            pixels.add((i, 17-i+d))
                for x, y in pixels:
                    tx = round(x * size / 16)
                    ty = round(y * size / 16)
                    thickness = max(1, size // 16)
                    if 2 <= tx < size-2 and 2 <= ty < size-2:
                        im.put(foreground, to=(tx, ty, min(size-2, tx+thickness), min(size-2, ty+thickness)))
            images.append(im)
        if element not in style.element_names():
            style.element_create(element, 'image', images[0], ('selected', images[1]))
        cache[key] = element, images  # Keep PhotoImage refs alive.
    element = cache[key][0]

    def swap_indicators(layout):
        out = []
        for name, opts in layout:
            info = dict(opts or {})
            if 'children' in info:
                info['children'] = swap_indicators(info['children'])
            if name.endswith('.indicator'):
                name = element
            out.append((name, info))
        return out
    style.layout(style_name, swap_indicators(style.layout('TCheckbutton')))



def _install_flat_scrollbar_thumb(root, style, thumb_color, active_color, style_prefix=''):
    """ttkの画像要素だけで横線のないつまみを作る（Canvas部品は不要）。

    Windows/OSのテーマは標準要素の見た目が異なるため、フラット表示は
    ttk.Style.layoutでthumb要素だけを差し替える。既存のスクロール操作は維持する。
    """
    holder = root._root()
    cache = getattr(holder, '_gds_flat_scrollbar_images', None)
    if cache is None:
        cache = {}
        holder._gds_flat_scrollbar_images = cache
    key = (thumb_color, active_color)
    if key not in cache:
        digest = hashlib.sha256(repr(key).encode('utf-8')).hexdigest()[:14]
        # ttk.Scrollbar は要素名の末尾「.thumb」を手掛かりに、
        # 表示割合からつまみの長さ・移動可能範囲を計算する。
        # この接尾辞がないと画像がレール全体に伸びてスクロールできなくなる。
        element = f'GDSFlatThumb{digest}.thumb'
        normal = tk.PhotoImage(master=holder, width=14, height=26)
        normal.put(thumb_color, to=(0, 0, 14, 26))
        active = tk.PhotoImage(master=holder, width=14, height=26)
        active.put(active_color, to=(0, 0, 14, 26))
        if element not in style.element_names():
            style.element_create(element, 'image', normal, ('active', active),
                                 border=(2, 2, 2, 2), sticky='nswe')
        cache[key] = (element, normal, active)
    thumb_element = cache[key][0]

    native = getattr(holder, '_gds_native_scroll_layouts', None)
    if native is None:
        native = {name: copy.deepcopy(style.layout(name)) for name in
                  ('Vertical.TScrollbar', 'Horizontal.TScrollbar')}
        holder._gds_native_scroll_layouts = native

    def replace_thumb(layout):
        result = []
        for name, options in layout:
            options = dict(options or {})
            if 'children' in options:
                options['children'] = replace_thumb(options['children'])
            if name.endswith('.thumb'):
                name = thumb_element
            result.append((name, options))
        return result

    for direction in ('Vertical', 'Horizontal'):
        base_style = f'{direction}.TScrollbar'
        names = [f'{style_prefix}.{base_style}' if style_prefix else base_style]
        if style_prefix:
            # ttk.Scrollbar may prepend the orientation to an explicit style name.
            names.append(f'{direction}.{style_prefix}.{base_style}')
        for name in names:
            style.layout(name, replace_thumb(native[base_style]))


def _restore_scrollbar_layout(root, style, style_prefix=''):
    """フラットから標準を選択した場合に、OS/Tkの元の要素へ戻す。"""
    holder = root._root()
    native = getattr(holder, '_gds_native_scroll_layouts', None)
    if native is None:
        native = {name: copy.deepcopy(style.layout(name)) for name in
                  ('Vertical.TScrollbar', 'Horizontal.TScrollbar')}
        holder._gds_native_scroll_layouts = native
    for direction in ('Vertical', 'Horizontal'):
        base_style = f'{direction}.TScrollbar'
        names = [f'{style_prefix}.{base_style}' if style_prefix else base_style]
        if style_prefix:
            names.append(f'{direction}.{style_prefix}.{base_style}')
        for name in names:
            style.layout(name, copy.deepcopy(native[base_style]))


def apply_theme(root, theme=None, *, style_prefix=""):
    """既存のTk/ttkアプリにテーマを適用し、ttk.Styleを返す。"""
    t = resolve_theme(theme)
    colors = t.get('colors', {})
    opts = t.get('options', {})
    c = lambda name, default: colors.get(name, default)
    v = lambda name, default: opts.get(name, default)
    density = v('density', 'normal')
    scale = {'compact': 0.75, 'normal': 1.0, 'spacious': 1.35}.get(density, 1.0)
    pad = lambda x: max(1, round(x * scale))
    font_family = v('font_family', 'Yu Gothic UI')
    font_size = int(v('font_size', 10))
    font = (font_family, font_size, v('font_weight', 'normal'))
    title_font = (font_family, int(v('title_size', 17)), v('title_weight', 'bold'))
    section_font = (font_family, int(v('section_size', 11)), v('section_weight', 'bold'))
    bg = c('background', '#F2F6FB')
    surface = c('surface', '#FFFFFF')
    surface_alt = c('surface_alt', '#E7EEF8')
    text = c('text', '#23344B')
    muted = c('muted', '#62758A')
    border = c('border', '#B9CADD')
    accent = c('accent', '#1765C7')
    hover = c('accent_hover', '#12519D')
    accent_text = c('accent_text', '#FFFFFF')
    field_bg = c('field_background', '#FFFFFF')
    select = c('selection', '#CDE1FF')
    success = c('success', '#387958')
    warning = c('warning', '#B47928')
    danger = c('danger', '#B84B50')
    # Editor/preview use a namespace so live preview never repaints the studio UI.
    # Exported standalone themes still use their normal ttk style names.
    if not style_prefix:
        root.configure(bg=bg)
    style = ttk.Style(root)
    if not style_prefix and 'clam' in style.theme_names():
        style.theme_use('clam')
    sn = lambda name: f'{style_prefix}.{name}' if style_prefix else name
    # 'OS標準' に戻せるよう、独自画像要素の適用前に元のレイアウトを保持する。
    holder = root._root()
    if not hasattr(holder, '_gds_native_check_layout'):
        holder._gds_native_check_layout = copy.deepcopy(style.layout('TCheckbutton'))
    frame_border = int(v('frame_border', 0))
    button_border = int(v('button_border', 1))
    input_border = int(v('input_border', 1))
    button_x = pad(int(v('button_padding_x', 14)))
    button_y = pad(int(v('button_padding_y', 8)))
    input_x = pad(int(v('input_padding_x', 8)))
    input_y = pad(int(v('input_padding_y', 6)))
    row_height = pad(int(v('row_height', 27)))
    button_style = v('button_style', 'raised')
    button_font = (font_family, font_size, v('button_text_weight', 'normal'))
    label_padding = (pad(int(v('label_padding_x', 0))), pad(int(v('label_padding_y', 0))))
    relief = {'flat': 'flat', 'raised': 'raised', 'outline': 'solid'}.get(button_style, 'raised')

    style.configure(sn('TFrame'), background=bg)
    style.configure(sn('App.TFrame'), background=bg)
    style.configure(sn('Card.TFrame'), background=surface, borderwidth=frame_border,
                    relief=v('frame_relief','solid') if frame_border else 'flat',
                    bordercolor=c(v('frame_color_role','border'),border))
    style.configure(sn('Alt.TFrame'), background=surface_alt)
    style.configure(sn('TLabel'), background=bg, foreground=text, font=font, padding=label_padding)
    style.configure(sn('Card.TLabel'), background=surface, foreground=text, font=font, padding=label_padding)
    style.configure(sn('Muted.TLabel'), background=bg, foreground=muted,
                    font=(font_family, int(v('muted_font_size',font_size)), v('font_weight','normal')),
                    padding=label_padding)
    style.configure(sn('Title.TLabel'), background=bg, foreground=c(v('title_color_role','text'),text),
                    font=title_font, padding=label_padding)
    style.configure(sn('Section.TLabel'), background=bg, foreground=c(v('section_color_role','text'),text),
                    font=section_font, padding=label_padding)
    style.configure(sn('Status.TLabel'), background=surface_alt, foreground=muted,
                    font=(font_family, int(v('status_font_size',font_size)), 'normal'),
                    padding=label_padding)
    style.configure(sn('Good.TLabel'), background=bg, foreground=success, font=font)
    style.configure(sn('Warning.TLabel'), background=bg, foreground=warning, font=font)

    style.configure(sn('TLabelframe'), background=bg, foreground=text,
                    bordercolor=c(v('frame_color_role','border'),border),
                    borderwidth=max(1, frame_border), relief=v('frame_relief','solid'),
                    padding=pad(int(v('group_padding', 10))))
    style.configure(sn('TLabelframe.Label'), background=bg, foreground=text, font=section_font)
    style.configure(sn('Card.TLabelframe'), background=surface, foreground=text,
                    bordercolor=c(v('frame_color_role','border'),border),
                    borderwidth=max(1, frame_border), relief=v('frame_relief','solid'),
                    padding=pad(int(v('group_padding', 10))))
    style.configure(sn('Card.TLabelframe.Label'), background=surface, foreground=text, font=section_font)

    style.configure(sn('TButton'), background=surface_alt, foreground=text, font=button_font,
                    padding=(button_x, button_y), relief=relief,
                    borderwidth=button_border, bordercolor=border)
    style.map(sn('TButton'), background=[('disabled', c(v('button_disabled_role','border'),border)),
                                      ('pressed', c(v('button_pressed_role','accent_hover'),hover)),
                                      ('active', c(v('button_hover_role','accent_hover'),hover))],
              foreground=[('disabled', muted), ('active', text)],
              relief=[('pressed', 'sunken')])
    style.configure(sn('Primary.TButton'), background=accent, foreground=accent_text, font=button_font,
                    padding=(button_x, button_y), relief=relief,
                    borderwidth=button_border, bordercolor=accent)
    style.map(sn('Primary.TButton'), background=[('disabled', c(v('button_disabled_role','border'),border)),
                                              ('pressed', c(v('button_pressed_role','accent_hover'),hover)),
                                              ('active', c(v('button_hover_role','accent_hover'),hover))],
              foreground=[('disabled', muted), ('active', accent_text)])
    style.configure(sn('Secondary.TButton'), background=surface, foreground=accent, font=button_font,
                    padding=(button_x, button_y), relief=relief,
                    borderwidth=max(1, button_border), bordercolor=accent)
    style.map(sn('Secondary.TButton'), background=[('active', c(v('button_hover_role','accent_hover'),hover)),
                                                    ('pressed', c(v('button_pressed_role','accent_hover'),hover))])
    style.configure(sn('Danger.TButton'), background=danger, foreground='#FFFFFF', font=button_font,
                    padding=(button_x, button_y), relief=relief, borderwidth=button_border)
    style.map(sn('Danger.TButton'), background=[('active', danger), ('pressed', danger)])

    input_font = (font_family, font_size, v('input_text_weight','normal'))
    style.configure(sn('TEntry'), font=input_font, foreground=text, fieldbackground=field_bg,
                    selectbackground=c(v('input_selection_role','selection'), select),
                    padding=(input_x, input_y), borderwidth=input_border, bordercolor=border,
                    insertcolor=text)
    style.map(sn('TEntry'), bordercolor=[('focus', c(v('input_focus_role','accent'), accent))],
              fieldbackground=[('disabled', c(v('input_disabled_bg_role','surface_alt'), surface_alt))])
    style.configure(sn('TCombobox'), font=input_font, foreground=text, fieldbackground=field_bg,
                    background=surface_alt, selectbackground=c(v('input_selection_role','selection'),select),
                    selectforeground=text, arrowsize=int(v('input_arrow_size',13)),
                    padding=(input_x, input_y), borderwidth=input_border,
                    bordercolor=border)
    # clamのreadonly状態でOSのデフォルト背景に戻り、文字が読めなくなるのを防ぐ。
    style.map(sn('TCombobox'), bordercolor=[('focus', accent)],
              fieldbackground=[('disabled', c(v('input_disabled_bg_role','surface_alt'), surface_alt)),
                               ('readonly', c(v('input_readonly_bg_role','field_background'),field_bg))],
              foreground=[('disabled', muted), ('readonly', text)],
              selectforeground=[('readonly', text)],
              selectbackground=[('readonly', c(v('input_readonly_bg_role','field_background'),field_bg))])
    style.configure(sn('TSpinbox'), font=input_font, foreground=text, fieldbackground=field_bg,
                    padding=(input_x, input_y), borderwidth=input_border)
    # チェック・ラジオはttk標準部品のまま文字色・太さ・余白を調整。
    # indicatorcolorはclamで対応する範囲のみ反映され、OSごとの差はあり得る。
    choice_fg = accent if v('choice_label_color', 'text') == 'accent' else text
    choice_weight = v('choice_font_weight', 'normal')
    choice_font = (font_family, int(v('choice_font_size', font_size)), choice_weight)
    choice_pad = (pad(int(v('choice_padding_x', 3))),
                  pad(int(v('choice_padding_y', 4))))
    indicator_map = ([('selected', accent)] if v('choice_indicator_color','default') == 'accent'
                     else [])
    for name, parent_bg in (('TCheckbutton', bg), ('TRadiobutton', bg),
                            ('Card.TCheckbutton', surface), ('Card.TRadiobutton', surface)):
        style.configure(sn(name), background=parent_bg, foreground=choice_fg,
                        font=choice_font, padding=choice_pad)
        style.map(sn(name), background=[('active', c(v('choice_active_bg_role','surface'), surface))],
                  foreground=[('disabled', c(v('choice_disabled_color_role','muted'), muted))],
                  indicatorcolor=indicator_map)
    style.configure(sn('TScale'), background=bg,
                    troughcolor=c(v('slider_track_color_role', 'surface_alt'), surface_alt),
                    bordercolor=border, borderwidth=int(v('slider_trough_border',1)),
                    slidercolor=c(v('slider_thumb_color_role','surface'), surface),
                    sliderlength=int(v('slider_thumb_size', 16)),
                    sliderthickness=int(v('slider_thumb_size', 16)))
    style.map(sn('TScale'), background=[('active', c(v('slider_active_role','accent'),accent))])
    style.configure(sn('Horizontal.TProgressbar'), background=c(v('progress_color_role','accent'), accent),
                    troughcolor=c(v('progress_trough_role','surface_alt'),surface_alt),
                    bordercolor=border, borderwidth=int(v('progress_border',1)),
                    thickness=int(v('progress_height', 13)))
    for name in ('Vertical.TScrollbar','Horizontal.TScrollbar'):
        style.configure(sn(name), background=c(v('scrollbar_thumb_role','surface_alt'),surface_alt),
                        troughcolor=c(v('scrollbar_trough_role','background'),bg),
                        arrowcolor=c(v('scrollbar_arrow_role','text'),text),
                        bordercolor=border, borderwidth=int(v('scrollbar_border',1)),
                        relief=v('scrollbar_relief','flat'), width=int(v('scrollbar_width', 14)))
        style.map(sn(name), background=[('active', c(v('scrollbar_active_role','selection'),select))])
    style.configure(sn('Treeview'), background=surface, fieldbackground=surface,
                    foreground=text, font=font, rowheight=row_height,
                    bordercolor=border, borderwidth=int(v('tree_border',1)))
    style.map(sn('Treeview'), background=[('selected', c(v('tree_selected_bg_role','selection'),select))],
              foreground=[('selected', c(v('tree_selection_text_role','text'), text))])
    style.configure(sn('Treeview.Heading'), background=surface_alt, foreground=text,
                    font=(font_family, int(v('section_size',11)), v('tree_heading_weight','bold')),
                    padding=(pad(int(v('tree_heading_padding_x',7))), pad(int(v('tree_heading_padding_y',5)))),
                    bordercolor=border)
    style.map(sn('Treeview.Heading'), background=[('active', select)])
    style.configure(sn('TNotebook'), background=bg, bordercolor=border,
                    borderwidth=int(v('notebook_border',1)))
    style.configure(sn('TNotebook.Tab'), background=surface_alt, foreground=text,
                    font=(font_family,font_size,v('tab_weight','normal')),
                    padding=(pad(int(v('tab_padding_x', 13))),
                                       pad(int(v('tab_padding_y', 7)))))
    style.map(sn('TNotebook.Tab'), background=[('selected', c(v('tab_selected_bg_role','surface'),surface)),
                                                     ('active', c(v('tab_active_role','selection'),select))],
              foreground=[('selected', c(v('tab_selected_text_role','accent'),accent))])

    # ttk.Scale / Progressbar / Scrollbar prepend their orientation internally
    # when given a custom style. Give those resolved names real layouts.
    if style_prefix:
        for custom, original, base_style in (
            ('Horizontal.' + sn('TScale'), 'Horizontal.TScale', sn('TScale')),
            ('Vertical.' + sn('TScale'), 'Vertical.TScale', sn('TScale')),
            ('Horizontal.' + sn('TProgressbar'), 'Horizontal.TProgressbar', sn('Horizontal.TProgressbar')),
            ('Vertical.' + sn('TScrollbar'), 'Vertical.TScrollbar', sn('Vertical.TScrollbar')),
            ('Horizontal.' + sn('TScrollbar'), 'Horizontal.TScrollbar', sn('Horizontal.TScrollbar')),
        ):
            style.layout(custom, style.layout(original))
            style.configure(custom, **style.configure(base_style))
            style.map(custom, **style.map(base_style))

    # フラット表示はttkのthumb画像要素を使用し、リストのスクロール機能は標準のまま。
    # 画像は同じTkルート内でキャッシュするため、プレビュー更新ごとに複製しない。
    if v('scrollbar_appearance', 'flat') == 'flat':
        _install_flat_scrollbar_thumb(root, style,
            c(v('scrollbar_thumb_role','surface_alt'), surface_alt),
            c(v('scrollbar_active_role','selection'), select), style_prefix)
    else:
        _restore_scrollbar_layout(root, style, style_prefix)

    # Standard ttk.Checkbutton with a selectable symbol. Only the small indicator
    # is supplied as a cached PhotoImage element; no Canvas widget is created.
    indicator_shape = v('choice_indicator_shape', 'check')
    if indicator_shape in ('check', 'cross'):
        for target, back in (('TCheckbutton', bg), ('Card.TCheckbutton', surface)):
            indicator_color = accent if v('choice_indicator_color', 'default') == 'accent' else text
            _install_check_indicator(root, style, sn(target), indicator_shape,
                                     indicator_color, back, border, v('choice_indicator_size',16))
    else:
        # 既に適用した画像要素から切替えても、本来のOS/Tkテーマ要素へ復元する。
        for target in ('TCheckbutton', 'Card.TCheckbutton'):
            style.layout(sn(target), copy.deepcopy(holder._gds_native_check_layout))

    # スタジオ自体の操作UI。濃色テーマでも編集用のプルダウン文字を常に読めるようにする。
    # プレビューの通常TComboboxには手を加えず、テーマの見た目を確認できるようにする。
    if style_prefix:
        return style
    editor_fg = '#20354E'
    editor_bg = '#FFFFFF'
    editor_border = '#8DAAC8'
    style.configure(sn('StudioEditor.TCombobox'), foreground=editor_fg,
                    fieldbackground=editor_bg, background='#E5EEF8',
                    selectforeground=editor_fg, selectbackground=editor_bg,
                    arrowcolor=editor_fg, bordercolor=editor_border)
    style.map(sn('StudioEditor.TCombobox'),
              foreground=[('disabled', '#6B7785'), ('readonly', editor_fg)],
              fieldbackground=[('disabled', '#F0F2F5'), ('readonly', editor_bg)],
              background=[('readonly', '#E5EEF8')],
              selectforeground=[('readonly', editor_fg)],
              selectbackground=[('readonly', editor_bg)])
    style.configure(sn('StudioEditor.TSpinbox'), foreground=editor_fg,
                    fieldbackground=editor_bg, background='#E5EEF8',
                    bordercolor=editor_border)
    style.map(sn('StudioEditor.TSpinbox'),
              foreground=[('disabled', '#6B7785')],
              fieldbackground=[('disabled', '#F0F2F5')])
    return style




def make_action_button(parent, text, command, theme=None, **kwargs):
    """標準ttk限定: 追加描画部品を使用せずボタンを生成する。"""
    return ttk.Button(parent, text=text, command=command,
                      style=kwargs.get('ttk_style', 'Primary.TButton'))


def make_value_slider(parent, variable, theme=None, **kwargs):
    """標準ttk限定: スライダーにはttk.Scaleを使用する。"""
    return ttk.Scale(parent, from_=0, to=100, variable=variable, orient='horizontal')
