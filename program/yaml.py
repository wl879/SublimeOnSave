
import re

YAML_ARR_SYMBLE = "_i_s_a_r_r_a_y_"

def parse( text ):
	text = re.sub(r'(?m)\s*#.*$|^\s*$', "", text)
	ref = {}
	level = -1
	level_stack = []
	parent_stack = []	
	lines = text.split("\n")
	for i in range(0, len(lines)):
		m = re.match(r'^(\s*)(-?)\s*([\w\d]*)\s*:\s*(.*)$', lines[i])
		if m:
			indent = len(re.sub(r'\t', "    ", m.group(1)))
			isarr  = m.group(2)
			name   = m.group(3)
			value  = m.group(4).strip()
		
			if level == -1:
				level_stack.append( indent )
			elif indent > level_stack[level]:
				level_stack.append( indent )	
			elif indent < level_stack[level]:
				while level >= 0 and indent <= level_stack[level]:
					level_stack.pop()
					level = len(level_stack) - 1
					if len(parent_stack) > 0:
						parent_stack.pop()
				level_stack.append(indent)
			else:
				parent_stack.pop()
			level = len(level_stack) - 1

			node = {}
			if isarr and name:
				node[name] = value or {}
			elif value:
				node = value

			if len(parent_stack) > 0:
				last = parent_stack[-1]
				if type(last) != dict:
					raise Exception("YAML File Error", '"'+lines[i]+'", line '+str(i+1))
				if isarr:
					if last.get(YAML_ARR_SYMBLE) == None:
						last[YAML_ARR_SYMBLE] = []
					last[YAML_ARR_SYMBLE].append(node)
				else:
					last[name] = node
			else:
				ref[name] = node
			parent_stack.append(node)
	_clearUp(ref)
	return ref
	
def _clearUp( data ):
	for k in data:
		if type(data[k]) != dict:
			continue
		if data[k].get(YAML_ARR_SYMBLE) != None:
			data[k] = data[k].get(YAML_ARR_SYMBLE)