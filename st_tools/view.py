# encoding: UTF-8
import sublime, sublime_plugin
import re, codecs, sys
from os import path

def create(name, win = None, group = None, file = None):
    if not win:
        win = sublime.active_window()
    focus_view = win.active_view()
    views = find(name, False, win)
    if not views:
        if group or group == 0:
            win.focus_group(group)
        view = win.new_file( )
        view.set_name( name )
    else:
        view = views[0]['view']
    if file:
        read(view, file)
    win.focus_view( view )
    if focus_view and focus_view.window():
        focus_view.window().focus_view(focus_view)
    return view

def setting(view, conf = {}, **_conf):
    exception = {
        "syntax"        : "assign_syntax",
        "assign_syntax" : "assign_syntax",
        "set_scratch"   : 'set_scratch',
        "scratch"       : 'set_scratch'
    }
    if sys.version_info < (3,0,0):
        exception['syntax'] = 'set_syntax_file'
    _conf.update(conf)
    settings = view.settings()
    for name in _conf:
        value = _conf[name]
        if name in exception:
            getattr(view, exception[name])(value)
            continue
        settings.set(name, value)

def find(name, one = True, win = None):
    windows = [win] if win else sublime.windows();
    lis = []
    for win in windows:
        views = win.views()
        for view in views:
            if view.name() == name:
                lis.append( {"window": win, "view": view} );
    if len(lis):
        if one:
            return lis[0]['view']
        return lis;

def read(file, view = None):
    if path.isfile(file):
        if not view:
            view = create( path.basename(file) )
        f = codecs.open(file, 'r', 'utf-8')
        text = f.read()
        f.close()
        view.run_command("insert_snippet", {"contents": text})
        return text

def content(view, text = None):
    if text:
        clear( view )
        view.run_command("insert_snippet", {"contents": text})
        return view
    return view.substr( sublime.Region(0, view.size()) )

def clear(view):
    view.run_command( "select_all" )
    view.run_command( "right_delete" )
    return view

def append(view, text, toend = False, refresh = False):
    view.run_command('append', {'characters': text, 'force': True, 'scroll_to_end': toend})
    view.show( view.layout_to_text( view.layout_extent() ) )
    if refresh:
        view.find_all_results()

def info(view):
    info = {}
    win = view.window()
    info['window'] = win
    info['index'] = win.get_view_index( view )
    layout = win.layout()
    cells  = layout['cells']
    for gid in range(0, len(cells)):
        if view in win.views_in_group( gid ):
            info['group'] = gid
            info['col'] = cells[gid][0]
            info['row'] = cells[gid][1]
            break
    return info;

def group(view, gid):
    win = view.window()
    sublime.set_timeout(lambda:  win.set_view_index(view, gid, 0), 100)