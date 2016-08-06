
import os
import codecs
import re
import json
from . import yaml

config_file_cache = {}
config_data_cache = {}


def scan( name, to_dir ):
	global config_file_cache
	depth = 10
	if os.path.isfile( to_dir ):
		to_dir = os.path.dirname(to_dir)
	work_dir = ''
	cache_keys = []
	while depth and to_dir and to_dir != '/':
		depth -= 1
		cache_keys.append(to_dir)
		if os.path.isfile( os.path.join(to_dir, name) ):
			work_dir = to_dir
			break
		if to_dir in config_file_cache:
			return config_file_cache[to_dir]
		to_dir =  os.path.dirname(to_dir)

	if work_dir:
		work_config = os.path.join(work_dir, name)
		for key in cache_keys:
			config_file_cache[key] = work_config
		return work_config
	
def read( name, to_dir = None ):
	global config_data_cache
	if to_dir:
		config_file = scan( name, to_dir )
	else:
		config_file = name

	if config_file:
		if config_file in config_data_cache:
			return config_data_cache[config_file]
		if os.path.isfile( config_file ):
			f = codecs.open( config_file, 'r', 'utf-8' )
			text = f.read().strip()
			f.close()
			if text[0] == '{':
				conf = json.loads( text )
			else:
				text = re.sub(r'(?m)WATCH\s*:\s*([^"\']*?)\s*$', 'WATCH : "\\1"', text)
				conf = yaml.load(text)
			conf[ '__file__' ] =  config_file
			conf[ '__dir__' ] =  os.path.dirname(config_file)
			config_data_cache[ config_file ] = conf
			return conf
	return ''

def refresh():
	global config_data_cache, config_file_cache
	config_data_cache = {}
	config_file_cache = {}