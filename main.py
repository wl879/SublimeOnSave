# encoding: UTF-8

import re, fnmatch
import sublime, sublime_plugin
from os import path
from . import st_tools
from .program import on_save

class OnSaveCommand(sublime_plugin.EventListener):

    def on_load(self, view):
        pass
        # file = view.file_name()
        # cmds = on_save.watch( file )
        # if cmds:
        #     for cmd in cmds:
        #         if cmd.get('usebuild'):
        #             view.settings().set('usebuild', True)
        #             return

    def on_post_save(self, view):
        file = view.file_name()
        if path.basename(file) == on_save.CONFIG_NAME:
            on_save.clear()
        else:
            cmds = on_save.watch( file )
            if cmds:
                on_save.run( cmds )

    # 检查 关闭输出窗口
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
    
    def run(self, paths):
        setting = sublime.load_settings('Default.sublime-settings')
        dir_path = paths[0]
        if path.isfile(paths[0]):
            dir_path = path.dirname(dir_path)
        if path.isfile( path.join(dir_path, on_save.CONFIG_NAME) ):
            view = self.window.open_file( path.join(dir_path, on_save.CONFIG_NAME) )
        else:
            view = st_tools.view.create( on_save.CONFIG_NAME, win = self.window )
            st_tools.view.content( view, '\n'.join( setting.get('config_template') or [] ) )
        if view:
            st_tools.view.setting(view, syntax = "Packages/YAML/YAML.tmLanguage", default_dir=dir_path)
        self.window.focus_view(view)

    def is_visible(self, paths):
        return len(paths) == 1

class OnSaveBuildCommand(sublime_plugin.WindowCommand):
   
    def run(self, paths):
        cmds = on_save.watch( paths[0] )
        if cmds:
            on_save.run( cmds )

    def is_visible(self, paths):
        if len(paths) == 1:
            if on_save.watch( paths[0] ):
                return True
        return False

# todo: 输出解析器是一个 正则配置，有： error, file, warn, log, tag, hide