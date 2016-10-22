# encoding: UTF-8

import re, fnmatch
import sublime, sublime_plugin
from os import path
from . import st_tools
from .program import OnSave

class OnSaveCommand(sublime_plugin.EventListener):

    def on_load(self, view):
        file = view.file_name()
        cmds = OnSave.watch( file )
        if cmds:
            for cmd in cmds:
                if cmd.get('usebuild'):
                    view.settings().set('usebuild', True)
                    return

    def on_post_save(self, view):
        file = view.file_name()
        if path.basename(file) == OnSave.configName:
            OnSave.refresh()
        else:
            cmds = OnSave.watch( file )
            if cmds:
                OnSave.cmd( cmds )

    # 检查 关闭输出窗口S
    def on_pre_close(self, view):
        name = view.name()
        if name and name.find('OnSave Console [') == 0:
            info = st_tools.view.info( view )
            if info:
                win = info['window']
                views = win.views_in_group( info['group'] )
                if not views or len(views) == 1:
                    sublime.set_timeout(lambda:  st_tools.group.delete(info['group'], win), 100)            

# 创建 OnSave 配置文件
class NewOnSaveConfigCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        setting = sublime.load_settings('Default.sublime-settings')
        if path.isfile( path.join(dirs[0], OnSave.configName) ):
            view    = self.window.open_file( path.join(dirs[0], OnSave.configName) )
        else:
            view = st_tools.view.create( OnSave.configName, win = self.window )
            st_tools.view.content( view, '\n'.join( setting.get('config_template') or [] ) )
        if view:
            st_tools.view.setting(view, syntax="Packages/YAML/YAML.tmLanguage", default_dir=dirs[0])
        self.window.focus_view(view)

    def is_visible(self, dirs):
        return len(dirs) == 1

class OnSaveBuild(sublime_plugin.TextCommand):
    
    def run(self, edit, **args):
        file = self.view.file_name()
        if path.basename(file) == OnSave.configName:
            OnSave.refresh()
        else:
            cmds = OnSave.watch( file )
            if cmds:
                OnSave.cmd( cmds, True)

