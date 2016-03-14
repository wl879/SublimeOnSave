# encoding: UTF-8
import sublime, sublime_plugin
import re, codecs
from os import path

def scanViews(name, window = None):
    if window:
        windows = [window]
    else:
        windows = sublime.windows();
    list = []
    for window in windows:
        views = window.views()
        for view in views:
        	if view.name() == name:
        		list.append( {"window": window, "view": view} );
    return list;

def createGroup(window, width = 0.3, at_left = False):
    layout = window.get_layout()

    if len(layout['rows']) > 2:
        return
    cells = layout['cells']
    cols  = layout['cols']
    num   = len(cells)
    tar   = None
    if num >= 1:
        for i in range(num-1, -1, -1):
            if len(window.views_in_group(i)) == 0:
                if i == 0 and at_left:
                    tar = i;
                    break;
                elif i == num-1 and not at_left:
                    tar = i
                    break;

    if tar == None:
        cell    = cells[-1][:]
        cell[0] += 1
        cell[2] += 1
        cells.append( cell )

        num = len(cells)-1
        move = width/num
        for i in range(1, num):
            if cols[i] - move > 0.05:
                cols[i] = cols[i] - move
            elif i < num:
                move += move/(num-i)
        if at_left:
            cols.insert(1, width)
        else:
            cols.insert(-1, 1-width)

    num   = len(cells)
    window.set_layout(layout)
    if at_left:
        window.focus_group(0)
        if tar == None:
            for g in range(num-2, -1, -1):
                views = window.views_in_group(g)
                for i in range(len(views)-1, -1, -1):
                    sublime.set_timeout(lambda:  window.set_view_index(views[i], g+1, 0), 100)
        return 0
    else:
        window.focus_group(num-1)
        return num-1

def create(name, window = None, conf = {}, **_conf):
    if not window:
        window = sublime.active_window()
    views = scanViews(name, window)
    _conf.update(conf)
    if len(views) == 0:
        if 'create_group' in _conf:
            createGroup(window)
        view = window.new_file()
        view.set_name(name)
        if len(_conf):
            setting(view, _conf)
    else:
        view = views[0]['view']

    if 'file' in _conf:
        readFile(_conf['file'], '', view)
    if 'text' in _conf:
        append(view, _conf['text'])
    return view

def setting(view, conf = {}, **_conf):
    short = {
        "num"          : "line_numbers",
        "read"         : "command_mode",
        "only_read"    : "command_mode",
        "font"         : "font_size",
        "file_point"   : "result_file_regex",
        "bar"          : "gutter",
        "tab"          : "tab_size",
        "top"          : "line_padding_top",
        "bottom"       : "line_padding_bottom",
        "encoding"     : "default_encoding",
        "dir"          : "default_dir",
        "create_group" : "",
        "file"         : "",
        "text"         : ""
    }
    exception = {
        "syntax" : "assign_syntax"
    }
    settings = view.settings()
    _conf.update(conf)
    for name in _conf:
        value = _conf[name]
        if name in exception:
            getattr(view, exception[name])(value)
            continue
        if name in short:
            name = short[name]
            if not name:
                continue;
        if name == 'result_file_regex':
            print(value)
        settings.set(name, value)

def findView(name, window = None):
    views = scanViews(name, window)
    if len(views):
        return views[0]['view']

def readFile(file, dir = '', view = None):
    if not path.isfile(file):
        file = path.join(dir, file)
    if path.isfile(file):
        f = codecs.open(file, 'r', 'utf-8')
        text = f.read()
        f.close()
        if view:
            view.run_command("insert_snippet", {"contents": text})
        return text

def content(view):
    return view.substr( sublime.Region(0, view.size()) )

def clear(view):
    view.run_command("select_all")
    view.run_command("right_delete")

def append(view, text, toend = False, refresh = False):
    view.run_command('append', {'characters': text, 'force': True, 'scroll_to_end': toend})
    view.show( view.layout_to_text( view.layout_extent() ) )
    if refresh:
        view.find_all_results()