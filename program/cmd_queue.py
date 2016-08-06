import os
from .cmd_console import Console

class CmdQueue():
    
    def __init__(self):
        self.queue    = {}
        self.consoles = {}

    def add(self, cmd):
        id = cmd.get('out');
        if not self.queue.get(id):
            self.queue[id] = []
        self.queue[ id ].append( cmd )
        self.check( id )

    def run(self, cmd):
        env     = cmd.get('env')
        out     = cmd.get('out')
        dir     = cmd.get('dir')
        timeout = cmd.get('timeout')
        os.chdir( dir )

        if out:
            console = self.consoles.get( out )
        if console:
            console.kill( 'stop' )
        else:
            console = Console( out, self )
        if out:
            self.consoles[ out ] = console
        console.run( cmd.get('cmd'), timeout, env)
        return console

    def check(self, id):
        queue = self.queue.get( id )
        if queue and queue[0]:
            if type(queue[0]) != Console:
                cmd = queue[0]
                queue[0] = self.run(cmd)
                return cmd
        return False;

    def next(self, id):
        queue = self.queue.get(id)
        if queue and queue[0]:
            if type(queue[0]) == Console:
                queue[0].kill()
                queue.pop(0)
            return self.check( id )
        return False

    def clear(self, id):
        if id:
            console = self.consoles.get(id)
            if console:
                console.clear();
            queue = self.queue.get( id )
            if queue:
                for item in queue:
                    if type(item) == Console:
                        item.kill( 'clear' )
            self.queue[id] = None
        else:
            for id in self.queue:
                self.clear( id )
            self.queue = {}