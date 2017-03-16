import re, fnmatch, sublime
from os import path
from .config import Config
from .cmd import Cmd
from .cmd_queue import CmdQueue

CMD_CACHE   = {}
CMD_QUEUE   = CmdQueue()
CONFIG_NAME = ".onsave"

def loadConfig(file):
	try:
		conf = Config.load(CONFIG_NAME, file)
		return conf
	except Exception as e:
		sublime.error_message( "On Save Error:\n{0}".format(e) )

def watch(file, from_keymap = False):
	global CMD_CACHE
	conf = loadConfig(file)
	if not conf:
		return
	if not from_keymap and CMD_CACHE.get(file):
		return CMD_CACHE.get(file)
	else:
		ref = []
		build = []
		rel_file = path.relpath(file, conf.dir)
		for listener in conf.listeners:
			if from_keymap:
				if listener.watch("BUILD"):
					build.append( Cmd.parse(file, listener) )
					continue
				if listener.watch("NOBUILD"):
					continue
			if listener.watch(rel_file):
				ref.append( Cmd.parse(file, listener) )
		if len(ref):
			CMD_CACHE[file] = ref
		if len(ref) or len(build):
			return ref + build

def run( cmds ):
	clear_list = []
	for cmd in cmds:
		console_id = cmd.console
		if console_id and console_id not in clear_list:
			CMD_QUEUE.clear( console_id )
			clear_list.append( console_id )
		CMD_QUEUE.add( cmd )

def clear():
	global CMD_CACHE
	Config.clear()
	CMD_CACHE = {}


