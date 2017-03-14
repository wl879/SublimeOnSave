import time, re, sublime
from Default import exec
from .. import st_tools

CONSOLE_LANGUAGE = "Packages/"+__package__.split('.')[0]+"/OnSave.tmLanguage"

class Console():

    def __init__(self, id):
        self.id       = id
        self.view     = None
        self.parser   = None
        self.encoding = 'UTF-8'

    def echo(self, text):
        if self.id and self.id.upper() != 'BACKGROUND':
            if self.view == None:
                self.view = Console.getView(self.id)
            st_tools.view.append(self.view, text, True)

    def log(self, text):
        if text.find('[now]') != -1:
            text = text.replace('[now]', time.strftime('%H:%M:%S'))
        self.echo( text+"\n" )
            
    def clear(self):
        if self.view:
            st_tools.view.clear( self.view );

    @staticmethod
    def getView( id ):
        title = "OnSave Console [" + id + "]"
        view = st_tools.view.find( title )
        if not view:
            settings = sublime.load_settings('Default.sublime-settings')
            win      = sublime.active_window()
            mode = 'right'
            if id.find('bottom') != -1:
                mode = 'bottom'
            elif id.find('left') != -1:
                mode = 'left'
            gid      = Console.getViewGroup(mode, win)
            view     = st_tools.view.create(title, win, group = gid)
            st_tools.view.setting(view, settings.get('console'), syntax = CONSOLE_LANGUAGE, scratch=True)
        return view;

    @staticmethod
    def getViewGroup( mode, win ):
        if not win:
            win = sublime.active_window()
        layout = win.layout()
        cells  = layout['cells']
        gid = st_tools.group.get(mode, win)
        if gid or gid == 0:
            views = win.views_in_group(gid)
            if not views or len(views) == 0:
                return gid
        info = st_tools.view.info( win.active_view() )
        return st_tools.group.create( mode, 0.3, win, 3, info['col'])
