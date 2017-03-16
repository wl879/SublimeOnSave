import os, time, sublime
from .console import Console
from Default import exec


class CmdQueue():
    
    def __init__(self):
        self.queue    = {}
        # self.consoles = {}

    def add(self, cmd):
        console_id = cmd.console
        if self.queue.get(console_id) == None:
            self.queue[console_id] = CmdProcess(console_id)
        self.queue[ console_id ].add( cmd )
        self.queue[ console_id ].check()

    def clear(self, console_id = None):
        if console_id:
            process = self.queue.get( console_id )
            if process:
                process.clear()
            self.queue[console_id] = None
        else:
            for console_id in self.queue:
                self.clear( console_id )
            self.queue = {}

class CmdProcess():

    def __init__(self, id):
        self.id = id
        self.queue   = []
        self.console = Console( self.id )
        self.process = None
        self.timestamp = 0
        self.timeoutId = 0

    def add(self, cmd):
        self.queue.append(cmd)

    def check(self):
        if self.process == None:
            self.run()
            return True
        return False;

    def run(self):
        if self.process != None:
            self.kill( "stop" )
        if len(self.queue) <= 0:
            return
        cmd = self.queue.pop(0)
        self.console.log('>>> # ' + cmd.cmd + '\n')
        if cmd.env and cmd.env.get("CWD"):
            os.chdir(cmd.env.get("CWD"))
        else:
            os.chdir(cmd.dir)
        self.process   = exec.AsyncProcess(None, cmd.cmd, cmd.env or {}, self)
        self.timestamp = self.process.start_time
        if cmd.timeout:
            timestamp = self.timestamp
            sublime.set_timeout(lambda:self.kill('timeout', timestamp), float(cmd.timeout))

    def kill(self, state = 'over', timestamp = None):
        if state == 'timeout' and timestamp != self.timestamp:
            return
        if self.process:
            exit_code = self.process.exit_code()
            if exit_code:
                self.console.log( "\n<<< ! Unexpected exit %d use %.2fs" % (exit_code, time.time() - self.timestamp) )
            elif exit_code != 0:
                self.console.log( "\n<<< ! Exit by %s use %.2fs" % (state, time.time() - self.timestamp) )
            self.process.kill()
        self.process = None

    # AsyncProcess 协议部分
    def on_data(self, process, data):
        text = data.decode( 'UTF-8' )
        self.console.echo( text )

    def on_finished(self, process):
        exit_code = process.exit_code()
        if exit_code == 0:
            self.console.log( "\n<<< # Finished use %.2fs\n" % (time.time() - self.timestamp) )
        else:
            self.console.log( "\n<<< ! Unexpected exit %d use %.2fs" % (exit_code, time.time() - self.timestamp) )
        self.process = None
        if len(self.queue) > 0:
            self.run()

    def clear(self):
        self.queue = []
        self.kill( "clear" )
        self.console.clear()
















