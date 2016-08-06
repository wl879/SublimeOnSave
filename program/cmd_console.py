import sys, os, time, re
import sublime
from Default import exec
from .. import st_tools

console_language = "Packages/"+__package__.split('.')[0]+"/OnSave.tmLanguage"

class Console():

    def __init__(self, id, queue):
        self.id       = id
        self.view     = None
        self.cmd      = None
        self.process  = None
        self.encoding = 'UTF-8'
        self.queue    = queue
        if id and id != 'Background':
            self.view = checkView(id)

    def run(self, cmd, timeout, env={}):
        print('[on save] [run] #', cmd)

        if self.view and not self.view.window():
            self.view = checkView( self.id )
            
        self.kill( 'check' )
        self.log('>>> # ' + cmd + '\n')
        self.cmd = cmd
        self.process = exec.AsyncProcess(None, cmd, env or {}, self)
        self.start_time = self.process.start_time
        timeout_id = time.time()
        self.timeout_id = timeout_id
        if timeout:
            sublime.set_timeout(lambda:self.kill('timeout', timeout_id), timeout)
        return self

    def kill(self, state = 'over', timeout_id = None):
        if state == 'timeout' and timeout_id != self.timeout_id:
            return
        if self.process:
            exit_code = self.process.exit_code()
            if exit_code:
                self.log( '\n<<< ! Unexpected exit '+str(exit_code)+' use %.2fs on [[now]]' )
            elif exit_code != 0:
                self.log( '\n<<< ! Exit by '+state+' use %.2fs on [[now]]' )
            self.process.kill()
        self.process = None
        return self

    # AsyncProcess 协议部分
    def on_data(self, process, data):
        if self.view:
            text = data.decode( self.encoding )
            self.echo( text )

    def on_finished(self, process):
        if self.view:
            exit_code = process.exit_code()
            if exit_code == 0:
                self.log( '\n<<< # Finished use %.2fs on [[now]]\n' )
            else:
                self.log( '\n<<< ! Unexpected exit'+str(exit_code)+' use %.2fs on [[now]]' )
        self.process = None
        if self.queue:
            self.queue.next( self.id )

    def echo(self, text):
        view = self.view
        st_tools.view.append(view, text, True)

    def log(self, msg):
        if self.view:
            if msg.find('%.2fs') != -1:
                msg = msg % (time.time() - self.start_time)
            if msg.find('[now]') != -1:
                msg = msg.replace('[now]', time.strftime('%H:%M:%S'))
            self.echo( msg+"\n" )

    def clear(self):
        if self.view:
            st_tools.view.clear( self.view );

def checkView( id ):
    global console_language
    view = st_tools.view.find( id )
    if not view:
        settings = sublime.load_settings('OnSave.sublime-settings')
        win      = sublime.active_window()
        mode = 'right'
        if id.find('bottom') != -1:
            mode = 'bottom'
        elif id.find('left') != -1:
            mode = 'left'
        gid      = checkGroup(mode, win)
        view     = st_tools.view.create(id, win, group = gid)
        st_tools.view.setting(view, settings.get('console'), syntax=console_language, scratch=True)
    return view;

def checkGroup( mode, win ):
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
