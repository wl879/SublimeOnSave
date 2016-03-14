# encoding: UTF-8

import sys, os, time, re, fnmatch
import sublime, sublime_plugin
from Default import exec
from os import path
try:
    from . import yaml
    from . import viewTools 
except (ImportError, ValueError):
    sublime.error_message('[OnSave cant import yaml module]')
    _stop = True

DEF_NAME      = '.onsave'
CONFIG_TMP    = path.dirname(__file__)+'/Config.TMP.yml'
SETTING       = sublime.load_settings('OnSave.sublime-settings')
BINS          = SETTING.get('bin') 
WORK_DIR      = {}
NOTWORK_DIR   = {}
CONFIG_CACHE  = {}
CMD_CACHE     = {}
PROCESS_CACHE = {}
CMD_QUEUE     = {}
RUN_QUEUE     = []

class NewOnSaveConfigCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        if path.isfile( path.join(dirs[0], DEF_NAME) ):
            view = self.window.open_file( path.join(dirs[0], DEF_NAME) )
        else:
            view = viewTools.create(DEF_NAME, self.window, text = '\n'.join(SETTING.get('config_template')))
        if view:
            viewTools.setting(view, syntax="Packages/YAML/YAML.tmLanguage", dir = dirs[0])

    def is_visible(self, dirs):
        return len(dirs) == 1

class OnSaveCommand(sublime_plugin.EventListener):
    
    def on_post_save(self, view):
        global RUN_QUEUE
        RUN_QUEUE = []
        file = view.file_name()

        if file in CMD_CACHE:
            print('[OnSave load cache] "'+file+'"')
            for cmd_opt in CMD_CACHE[file]:
                pushCMDQueue( cmd_opt )
            return

        if path.basename(file) == DEF_NAME:
            refreshOnSaveConfig( path.dirname(file) )
            return

        work_dir = checkOnSaveWorkDir(file)
        if checkOnSavePattern( viewTools.content(view), file, work_dir):
            return

        if file in NOTWORK_DIR:
            return

        if work_dir:
            config = loadOnSaveConfig(work_dir)
            if config:
                print('[OnSave run file] "'+file+'"')
                parseOnSaveConfig(config, work_dir, file)
                return

        print('[OnSave exclude file] "'+file+'"')
        NOTWORK_DIR[file] = True

class ProcessListener(object):

    def __init__(self, cmd, debug_id, view = None, env = {}, encoding = "utf-8"):
        self.debugID  = debug_id
        self.view     = view
        self.process  = None
        self.runtime  = 0
        self.encoding = encoding
        self.run(cmd, env)

    def run(self, cmd, env={}):
        self.message('>>> # '+cmd)
        self.process = exec.AsyncProcess(None, cmd, env or {}, self)
        self.start_time = self.process.start_time
        self.runtime += 1
        return self

    def kill(self, msg = None):
        if self.process:
            exit_code = self.process.exit_code()
            if exit_code == None or exit_code:
                self.message( '\n>>> ! Unexpected exit'+str(exit_code)+' use %.2fs on [[now]]' )
            self.process.kill()
        self.process = None
        return self

    def on_data(self, process, data):
        if self.view:
            text = data.decode( self.encoding )
            ehcoText( self.view, text )

    def on_finished(self, process):
        if self.view:
            exit_code = process.exit_code()
            if exit_code == 0:
                self.message( '\n>>> # Finished use %.2fs on [[now]]\n' )
            else:
                self.message( '\n>>> ! Unexpected exit'+str(exit_code)+' use %.2fs on [[now]]' )
        self.process = None
        if not checkCMDQueue(self.debugID, True):
            killProcessor( self.debugID )

    def message(self, msg):
        if self.view:
            if msg.find('%.2fs') != -1:
                msg = msg % (time.time() - self.start_time)

            if msg.find('[now]') != -1:
                msg = msg.replace('[now]', time.strftime('%H:%M:%S'))
            ehcoText(self.view, msg+"\n")

def refreshOnSaveConfig(work_dir):
    global CMD_CACHE, NOTWORK_DIR
    CMD_CACHE = {}
    NOTWORK_DIR = {}
    loadOnSaveConfig(work_dir, True)
    print('[OnSave config refresh] "'+work_dir+'"')

def checkOnSaveWorkDir(to):
    if to in WORK_DIR:
        return WORK_DIR[to]

    work_dir = ''
    subs     = [to]
    for loop in range(10):
        to = path.dirname(to)
        if not to or to == '/':
            return;
        if to in WORK_DIR:
            work_dir = WORK_DIR[to]
            break;
        subs.append(to)
        if path.isfile(to + '/' + DEF_NAME):
            work_dir = to
            break;

    if work_dir:
        for p in subs:
            WORK_DIR[p] = work_dir
        return work_dir

def checkOnSavePattern(text, file, work_dir):
    m = re.findall(r'(?m)\#\s*(CMD|DEBUG|ENV)\s*:\s*(.*?)$', text)
    listeners = []
    block     = ''
    for item in m:
        if item[0] == 'CMD':
            if block:
                listeners.append( yaml.load(block) )
            block = item[0]+' : '+item[1]
        else:
            block += "\n"+item[0]+' : '+item[1]
    if block:
        listeners.append( yaml.load(block) )

    work_dir = work_dir or path.dirname(file)
    for item in listeners:
        cmd_opt = parseListener(item, file, work_dir)
        if cmd_opt:
            pushCMDQueue( cmd_opt )

def loadOnSaveConfig(work_dir, reload = False):
    if reload == False and work_dir in CONFIG_CACHE and CONFIG_CACHE[work_dir]:
        return CONFIG_CACHE[work_dir]
    conf_file = work_dir+'/'+DEF_NAME
    conf_text = viewTools.readFile(conf_file)
    if conf_text:
        conf_text = re.sub(r'(?m)WATCH\s*:\s*([^"\'].*?)\s*$', 'WATCH : "\\1"', conf_text)
        conf = yaml.load(conf_text)
        if conf:
            CONFIG_CACHE[work_dir] = conf
            return conf
        print('[OnSave config parse error!!] "'+conf_file+'"')
        sublime.error_message('[OnSave config parse error!!] "'+conf_file+'"')

def parseOnSaveConfig(config, work_dir, file):
    relative  = file[len(work_dir)+1:]
    listeners = config.get('LISTENER') or []
    param     = config.get('VAR') or {}
    for item in listeners:
        if not item.get('CMD'):
            continue

        if item.get('WATCH'):
            if not checkWatch( item['WATCH'], relative):
                continue

        cmd_opt = parseListener(item, file, work_dir, param, config)
        pushCMDQueue( cmd_opt )

        if file not in CMD_CACHE:
            CMD_CACHE[file] = []
        for data in CMD_CACHE[file]:
            if cmd_opt['cmd'] == data['cmd']:
                cmd_opt = None
        if cmd_opt:
            CMD_CACHE[file].append( cmd_opt )

def parseListener(listener, file = '', work_dir = '', param = None, config = {}):
    cmd = listener.get('CMD')
    if not cmd:
        return None
    
    if param:
        cmd = re.sub(r'\$(\w+)', lambda m: param.get(m.group(1), m.group(0)), cmd)

    cmd = re.sub(r'^(\w+)(?# |$)', lambda m: BINS.get(m.group(1), m.group(0)), cmd)
    cmd = re.sub(r'\$FILEDIR\b', path.dirname(file), cmd)
    cmd = re.sub(r'\$FILENAME\b', path.basename(file), cmd)
    cmd = re.sub(r'\$FILE\b', file, cmd)
    cmd = re.sub(r'\$ROOT\b', work_dir, cmd)

    debug = listener.get('DEBUG') or config.get('DEBUG')
    env   = listener.get('ENV') or config.get('ENV')
    timeout = listener.get('TIMEOUT')
    return {"cmd":cmd, "debugID": debugID(debug or 0), "file":file, "work_dir":work_dir, "env":env, "timeout":timeout}

def pushCMDQueue( cmd_opt ):
    debug_id = cmd_opt.get('debugID');
    if debug_id:
        if debug_id not in RUN_QUEUE:
            RUN_QUEUE.append(debug_id)
            CMD_QUEUE[debug_id] = []
            killProcessor(debug_id)

        CMD_QUEUE[debug_id].append( cmd_opt )
        checkCMDQueue(debug_id)
    else:
        runCMD(debug_id, cmd_opt)

def checkCMDQueue(debug_id, check_next = False):
    cmd_list = CMD_QUEUE.get(debug_id)
    if cmd_list and len(cmd_list):
        is_queue = False
        if check_next and cmd_list[0] == 'Runing': 
            cmd_list.pop(0)
            is_queue = True

        if len(cmd_list) == 0:
            return False;

        if cmd_list[0] != 'Runing':
            cmd_opt = cmd_list[0]
            runCMD(debug_id, cmd_opt, is_queue)
            cmd_list[0] = 'Runing'
            return True
    return False;

def runCMD(debug_id, cmd_opt, need_queue = False):
    cmd      = cmd_opt.get('cmd')
    work_dir = cmd_opt.get('work_dir')
    env      = cmd_opt.get('env')
    print('[OnSave CMD] '+cmd)

    if work_dir:
        os.chdir(work_dir)

    processor = PROCESS_CACHE.get(debug_id)
    if processor:
        if need_queue and processor.debugID == debug_id:
            processor.kill().run(cmd, env);
            return
        processor.kill()
        PROCESS_CACHE[debug_id] = None

    if debug_id == 'OnSave Default':
        processor = ProcessListener(cmd, debug_id, None, env)

    elif debug_id[0] == '#':
        window = sublime.active_window()
        panel = window.create_output_panel("exec")
        viewTools.setting(panel, SETTING.get('console'))
        window.run_command("show_panel", {"panel": "output.exec"})
        processor = ProcessListener(cmd, debug_id, panel, env)

    else:
        view = checkView(debug_id)
        if not need_queue and debug_id.find('refresh') != -1:
            viewTools.clear(view)
        processor = ProcessListener(cmd, debug_id, view, env)

    PROCESS_CACHE[debug_id] = processor
    if cmd_opt.get('timeout'):
        sublime.set_timeout(lambda:killProcessor(debug_id), cmd_opt.get('timeout'))

def killProcessor(debug_id):
    if PROCESS_CACHE.get(debug_id):
        PROCESS_CACHE[debug_id].kill()
        PROCESS_CACHE[debug_id] = None

def ehcoText(view, text):
    text = re.sub(r'(?m)^(?!>>>|\[(\W){4}\]|$)', '    ', text)
    if re.search(r'\[(\W){4}\]', text):
        num = int((view.viewport_extent()[0]/view.em_width())-2)
        text = re.sub(r'\[(\W){4}\]', lambda m:(m.group(1) * num), text)
    viewTools.append(view, text, True)

def checkView(name):
    view = viewTools.findView(name)
    if not view:
        old_view = sublime.active_window().active_view()
        view = viewTools.create(name , None, SETTING.get('console'), create_group = True)
        if sys.version_info < (3,0,0):
            view.set_syntax_file("Packages/"+__package__+"/OnSave.tmLanguage")
        else:
            view.assign_syntax("Packages/"+__package__+"/OnSave.tmLanguage")
        view.set_scratch(True)
        old_view.window().focus_view(old_view)
    return view;

def checkWatch(patt, file):
    patts = patt.split(', ')
    for patt in patts:
        watch = pathToRe(patt)
        if watch.search(file):
            return True
    return False

def pathToRe(s):
    s = fnmatch.translate(s)
    s = re.sub(r'(?<!\\)\[(\(.*?(?<!\\)\))(?<!\\)\]', "\\1", s)
    s = re.sub(r'(?<!\\)\[\*\/\]', "[^\\/]*", s)
    return re.compile( s )

def debugID(debug):
    if not debug:
        return 'OnSave Default'
    if isinstance(debug, str):
        debug_id = 'OnSave Console'
        if debug != 'console':
            debug_id += ' ['+debug+']'
        return debug_id
    else:
        return '#OnSave Console ['+str(sublime.active_window().id())+']'

