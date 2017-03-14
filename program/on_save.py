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
		sublime.error_message( "On Save\nload config error:\n{0}".format(e) )

def watch(file):
	global CMD_CACHE
	if CMD_CACHE.get(file):
		return CMD_CACHE.get(file)
	else:
		conf = loadConfig(file)
		if conf:
			rel_file = path.relpath(file, conf.dir)
			listeners = conf.watch(rel_file)
			if listeners:
				if CMD_CACHE.get(file) == None:
					CMD_CACHE[ file ] = []
				for listen in listeners:
					cmd = Cmd.parse(file, listen)
					for item in CMD_CACHE[ file ]:
						if cmd.cmd == item.cmd:
							cmd = None
							break
					if cmd:
						CMD_CACHE[ file ].append( cmd )      
				return CMD_CACHE[file] if len(CMD_CACHE[file]) > 0 else None

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


