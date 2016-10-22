import re, fnmatch
from os import path
from .. import st_tools
from .cmd_cache import CmdCache
from .cmd_queue import CmdQueue
from .cmd_console import Console

CMD_CACHE     = CmdCache()
CMD_QUEUE     = CmdQueue()

class OnSave():

	configName = ".onsave"

	@staticmethod
	def config(file, match = False):
		config = st_tools.config.read(OnSave.configName, file)
		if config:
			if match:
				listeners = []
				lis       = config.get('LISTENER') or []
				file      = file[ len(config['__dir__'])+1: ]
				for item in lis:
					if item.get('CMD'):
						if matchFile( item.get('WATCH'), file ):
							listeners.append(item)
				return config, listeners
		return config, None

	@staticmethod
	def watch(file):
		if CMD_CACHE.get(file):
			return CMD_CACHE.get(file)
		else:
			config, listeners = OnSave.config(file, True)
			if listeners:
				for listener in listeners:
					CMD_CACHE.addListener( file, listener, config )
				return CMD_CACHE.get(file)	

	@staticmethod
	def cmd( cmds, usebuild = False ):
		clear_list = []
		for cmd in cmds:
			if usebuild:
				if not cmd.get('usebuild'):
					continue
			elif cmd.get('usebuild'):
				continue
			console_id = cmd.get('out')
			if console_id and console_id not in clear_list:
				CMD_QUEUE.clear( console_id )
				# st_tools.view.clear( st_tools.view.find(console_id) )
				clear_list.append( console_id )
			CMD_QUEUE.add( cmd )

	@staticmethod
	def refresh():
		st_tools.config.refresh()
		CMD_CACHE.refresh()

def matchFile( patt, file ):
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