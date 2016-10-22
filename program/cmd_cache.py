
import re
from os import path

class CmdCache( ):

    def __init__(self):
        self.cache = {}

    def addListener(self, file, listener, config):
        dir       = config['__dir__']
        variables = config.get('VAR')
        cmd       = listener.get('CMD')
        out       = listener.get('OUT') if 'OUT' in listener else config.get('OUT')
        env       = listener.get('ENV') or config.get('ENV')
        timeout   = listener.get('TIMEOUT') or config.get('TIMEOUT') or None
        paser     = listener.get('PASER') or ""
        usebuild  = listener.get('USEBUILD') or False
        if variables:
            cmd = re.sub(r'\$(\w+)', lambda m: variables.get(m.group(1), m.group(0)), cmd)
        cmd = re.sub(r'\$FILEDIR\b', path.dirname(file), cmd)
        cmd = re.sub(r'\$FILENAME\b', path.basename(file), cmd)
        cmd = re.sub(r'\$FILE\b', file, cmd)
        cmd = re.sub(r'\$ROOT\b', dir, cmd)
        return self.add( file, cmd, dir, out, env, timeout, paser, usebuild )

    def add(self, file, cmd, dir, out, env, timeout = None, paser = "", usebuild = False):
        out = 'OnSave Console ['+str(out)+']' if out else 'Background'
        cmd = { "cmd" : cmd,  "out" : out, "file" : file, "dir" : dir,  "env" : env,
                "timeout" : timeout, "paser":paser, "usebuild":usebuild}
        if not self.cache.get(file):
            self.cache[ file ] = []
        for item in self.cache[file]:
            if cmd['cmd'] == item['cmd']:
                return item
        self.cache[ file ].append( cmd )
        return cmd;

    def get(self, file):
        return self.cache.get( file )

    def refresh(self):
        self.cache = {}