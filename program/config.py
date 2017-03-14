
from os import path
import codecs, re, fnmatch, json
from . import yaml

FILE_CACHE = {}
DATA_CACHE = {}

class Config():

	def __init__(self, file):

		self.file = file
		self.dir = path.dirname(file)
		
		f = codecs.open( file, 'r', 'utf-8' )
		text = f.read().strip()
		f.close()
		self.data = json.loads( text ) if text[0] == '{' else yaml.parse( text )			
		
		self.listeners = []
		for sub in self.data.get('LISTENER') or []:
			if sub.get("CMD"):
				self.listeners.append( Listener(sub, self) )

	def get(self, name):
		if name == "CONSOLE":
			return self.data.get(name) or self.data.get("OUT")
		return self.data.get(name)

	def watch(self, file):
		res = []
		for l in self.listeners:
			if l.watch(file):
				res.append(l)
		return res if len(res) > 0 else None

	@staticmethod
	def scan(target, filename, uplevel = 10):
		global FILE_CACHE
		if path.isfile( target ):
			target = path.dirname(target)
		project_dir = ''
		sub_dirs = []
		while uplevel and target and target != '/':
			uplevel -= 1
			sub_dirs.append( target )
			if path.isfile( path.join(target, filename) ):
				config_path = path.join(target, filename)
				for key in sub_dirs:
					FILE_CACHE[key] = config_path
				return config_path

			if target in FILE_CACHE:
				return FILE_CACHE[target]
			target = path.dirname(target)

	@staticmethod
	def load( filename, dirname = None ):
		global DATA_CACHE
		config_path = Config.scan(dirname, filename) if dirname else filename
		if config_path:
			if config_path in DATA_CACHE:
				return DATA_CACHE[config_path]

			if path.isfile( config_path ):
				config = Config(config_path)
				DATA_CACHE[ config_path ] = config
				return config

	@staticmethod
	def clear():
		global DATA_CACHE, FILE_CACHE
		DATA_CACHE = {}
		FILE_CACHE = {}
		
class Listener():
	def __init__(self, data, root):
		self.root     = root
		self.data     = data
		self._watch   = prasePattern( data.get('WATCH') )
		self._exclude = prasePattern( data.get('EXCLUDE') )
	
	def get(self, name):
		if name == "CONSOLE":
			return self.data.get(name) or self.data.get("OUT")
		return self.data.get(name)

	def watch(self, file) :
		if len(self._exclude) == 0 and len(self._watch) == 0:
			return True
		for ex in self._exclude:
			if ex.search(file):
				return False
		for wa in self._watch:
			if wa.search(file):
				return True
		return False

def prasePattern( patt ):
	res = []
	if patt:
		for patt in patt.split(', '):
			patt = re.sub(r'(?<!\\|\[)(\(.*?(?<!\\)\))(?<!\\)', "[\\1]", patt)
			patt = fnmatch.translate(patt)
			patt = re.sub(r'(?<!\\)\[(\(.*?(?<!\\)\))(?<!\\)\]', "\\1", patt)
			patt = re.sub(r'(?<!\\)\[\*\/\]', "[^\\/]*", patt)
			res.append( re.compile( patt ) )
	return res
