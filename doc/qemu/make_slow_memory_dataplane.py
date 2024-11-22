#!/usr/bin/python3

import os
import sys

ANSI_COLOR_RED = "\x1b[31m"
ANSI_COLOR_GREEN = "\x1b[32m"
ANSI_COLOR_YELLOW = "\x1b[33m"
ANSI_COLOR_RESET = "\x1b[0m"


def ReadChanges():
	path_changes = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'changes.txt')
	if not os.path.exists(path_changes):
		print(f'Not found file: {path_changes}')
		sys.exit(1)
	
	with open(path_changes) as f:
		nl = 0
		changes = dict()
		for line in f:
			nl += 1
			if line.strip() == '':
				continue
			parts = [part.strip() for part in line.strip().split('\t') if part.strip() != '']
			if len(parts) != 3:
				print(f'Bad format line {nl}:\n{line}')
				sys.exit(1)
			name, old_value, new_value = parts
			changes[name] = (old_value, new_value)
		return changes

def ApplyChanges(changes):
	path_config = 'config.release.h'
	if not os.path.exists(path_config):
		print(f'Not found file: {path_config}')
		sys.exit(1)
	
	changed = False
	new_text = ''
	found = set()
	with open(path_config) as f:
		nl = 0
		for line in f:
			nl += 1
			s = line.rstrip()
			for name, values in changes.items():
				prefix = f'#define {name} '
				if line.startswith(prefix):
					found.add(name)
					old_value, new_value = values
					right = s[len(prefix):].strip()
					action = 'OK'
					if right == old_value:
						s = prefix + new_value
						changed = True
						color = ANSI_COLOR_GREEN
					elif right == new_value:
						action = 'Changed earlier'
						color = ANSI_COLOR_YELLOW
					else:
						action = f'Unknown value: {right}'
						color = ANSI_COLOR_RED
					print(f'{name:40} {color}{action}{ANSI_COLOR_RESET}')
			new_text += s + '\n'

	for name in changes.keys():
		if name not in found:
			print(f'{name:40} {ANSI_COLOR_RED}not found{ANSI_COLOR_RESET}')

	if changed:
		with open(path_config, 'w') as f:
			f.write(new_text)
		print('\nFile updated!')

if __name__ == '__main__':
	changes = ReadChanges()
	ApplyChanges(changes)
