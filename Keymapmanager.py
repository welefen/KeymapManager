import sublime, sublime_plugin
import os
import json

class KeymapmanagerCommand(sublime_plugin.TextCommand):
	"""
	keymap manager for plugins
	"""
	#ignore dirs
	ignoreDirs = [
		"CSS", "Vintage", "User", "Default"
	]
	#add system command to keymap manager
	sysCommand = [
		{"name": "Goto Anything...", "window": True, "keys": ["ctrl+p"], "command": "show_overlay", "args": {"overlay": "goto", "show_files": True} },
		{"name": "Command Palette",  "window": True,"keys": ["ctrl+shift+p"], "command": "show_overlay", "args": {"overlay": "command_palette"} },
		{"name": "Goto Symbol...", "window": True,"keys": ["ctrl+r"], "command": "show_overlay", "args": {"overlay": "goto", "text": "@"} },
		{"name": "Goto Line...", "window": True, "keys": ["ctrl+g"], "command": "show_overlay", "args": {"overlay": "goto", "text": ":"} },
		{"name": "Search Keywords", "window": True,"keys": ["ctrl+;"], "command": "show_overlay", "args": {"overlay": "goto", "text": "#"} },
		{"name": "Show Console", "window": True, "keys": ["ctrl+`"],  "command": "show_panel", "args": {"panel": "console", "toggle": True} }

	]
	#installed plugins list
	plugins = None

	def run(self, edit):
		if self.plugins == None:
			self.plugins = []
		path = sublime.packages_path()
		dirs = os.listdir(path)
		plugins = []
		for name in dirs:
			if name in self.ignoreDirs:
				continue
			dir = path + '/' + name + '/'
			if not os.path.isdir(dir):
				continue
			platform = sublime.platform()
			platform = platform[0].upper() + platform[1:].lower()
			keymapFile = dir + "Default (" + platform + ").sublime-keymap"
			if not os.path.isfile(keymapFile):
				continue
			#plugins.append(keymapFile)
			with open(keymapFile) as f:
				content = open(keymapFile).read()
			jsonData = json.loads(content)
			if not isinstance(jsonData, list):
				continue
			i = 0
			for item in jsonData:
				if i >= 3:
					break
				if "keys" not in item or "command" not in item:
					continue
				keys = item["keys"]
				if isinstance(keys, list):
					keys = ", " . join(keys)
				command = item["command"]
				item["name"] = name
				plugins.append([name, command + " : " +  keys])
				self.plugins.append(item)
				i += 1
		for item in self.sysCommand:
			plugins.append([item['name'], item['command'] + " : " +  ",".join(item['keys'])])
			self.plugins.append(item)

		self.view.window().show_quick_panel(plugins, self.panel_done)

	#panel done
	def panel_done(self, picked):
		if picked == -1:
			return 
		item = self.plugins[picked]
		if self.checkContext(item) == False:
			return
		args = {}
		if "args" in item:
			args = item['args']
		#thanks for wuliang
		self.view.run_command(item['command'], args)
		self.view.window().run_command(item['command'], args)
		sublime.run_command(item['command'], args)
		#if "window" in item and item['window'] == True:
		#	self.view.window().run_command(item['command'], args)
		#else:
		#	self.view.run_command(item['command'], args)
	#check context condition
	def checkContext(self, plugin):
		return True
		#if "context" not in plugin:
		#	return True
		if "window" in plugin and plugin["window"]:
			return True
		#context = plugin["context"]
		name = plugin["name"]
		path = path = sublime.packages_path() + '/' + name + '/'
		import glob
		pyFiles = glob.glob("*.py")
		sublime.status_message(",".join(pyFiles))
		return True
