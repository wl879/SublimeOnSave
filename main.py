# encoding: UTF-8

import re, fnmatch
import sublime, sublime_plugin
from os import path
from . import st_tools
from . import program

DEF_NAME      = '.onsave'
CMD_CACHE     = program.CmdCache()
CMD_QUEUE     = program.CmdQueue()

class OnSaveCommand(sublime_plugin.EventListener):

    def on_post_save(self, view):
        global CMD_CACHE, DEF_NAME
        file = view.file_name()
        if path.basename(file) == DEF_NAME:
            st_tools.config.refresh()
            CMD_CACHE.refresh()
        else:
            cmds = self.watch( file )
            if cmds:
                self.console( cmds )

    def on_pre_close(self, view):
        name = view.name()
        if name and name.find('OnSave Console [') == 0:
            info = st_tools.view.info( view )
            if info:
                win = info['window']
                views = win.views_in_group( info['group'] )
                if not views or len(views) == 1:
                    sublime.set_timeout(lambda:  st_tools.group.delete(info['group'], win), 100)


    def config(self, file):
        global DEF_NAME
        return st_tools.config.read(DEF_NAME, file)

    def watch(self, file):
        global CMD_CACHE
        if CMD_CACHE.get(file):
            return CMD_CACHE.get(file)
        else:
            config = self.config( file )
            if config:
                listeners = config.get('LISTENER') or []
                relative  = file[ len(config['__dir__'])+1: ]
                for listener in listeners:
                    if listener.get('CMD'):
                        if watchFile( listener.get('WATCH'), relative ):
                            CMD_CACHE.addListener( file, listener, config )
                return CMD_CACHE.get(file)
                
    def console(self, cmds):
        clear_list = []
        for cmd in cmds:
            console_id = cmd.get('out')
            if console_id and console_id not in clear_list:
                CMD_QUEUE.clear( console_id )
                # st_tools.view.clear( st_tools.view.find(console_id) )
                clear_list.append( console_id )
            CMD_QUEUE.add( cmd )



# 创建 OnSave 配置文件
class NewOnSaveConfigCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        setting = sublime.load_settings('OnSave.sublime-settings')
        if path.isfile( path.join(dirs[0], DEF_NAME) ):
            view    = self.window.open_file( path.join(dirs[0], DEF_NAME) )
        else:
            view = st_tools.view.create( DEF_NAME, win = self.window )
            st_tools.view.content( view, '\n'.join( setting.get('config_template') or [] ) )
        if view:
            st_tools.view.setting(view, syntax="Packages/YAML/YAML.tmLanguage", default_dir=dirs[0])
        self.window.focus_view(view)

    def is_visible(self, dirs):
        return len(dirs) == 1

def watchFile( patt, file ):
    if not patt:
        return True
    patts = patt.split(', ')
    for patt in patts:
        patt = fnmatch.translate(patt)
        patt = re.sub(r'(?<!\\)\[(\(.*?(?<!\\)\))(?<!\\)\]', "\\1", patt)
        patt = re.sub(r'(?<!\\)\[\*\/\]', "[^\\/]*", patt)
        watch = re.compile( patt )
        if watch.search(file):
            return True
    return False
