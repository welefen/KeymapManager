import sublime, sublime_plugin
import os
import json

settings = sublime.load_settings("KeymapManager.sublime-settings")

class KeymapManagerCommand(sublime_plugin.TextCommand):
	"""
	keymap manager for plugins
	"""
	#add some default very usefull commands
	defaultCommand = [
		{"name": "Goto Anything...", "keys": ["ctrl+p"], "command": "show_overlay", "args": {"overlay": "goto", "show_files": True} },
		{"name": "Command Palette", "keys": ["ctrl+shift+p"], "command": "show_overlay", "args": {"overlay": "command_palette"} },
		{"name": "Goto Symbol...", "keys": ["ctrl+r"], "command": "show_overlay", "args": {"overlay": "goto", "text": "@"} },
		{"name": "Goto Line...",  "keys": ["ctrl+g"], "command": "show_overlay", "args": {"overlay": "goto", "text": ":"} },
		{"name": "Search Keywords", "keys": ["ctrl+;"], "command": "show_overlay", "args": {"overlay": "goto", "text": "#"} },
		{"name": "Show Console",  "keys": ["ctrl+`"],  "command": "show_panel", "args": {"panel": "console", "toggle": True} }
	]
	#installed plugins list
	plugins = None

	def run(self, edit):
		self.defaultCommand.sort(key=lambda x: x["name"].lower())
		
		if self.plugins == None:
			self.plugins = []
		path = sublime.packages_path()
		dirs = os.listdir(path)
		#sort with insensitive
		dirs.sort(key=lambda x: x.lower())
		plugins = []
		ignored_packages = settings.get("ignored_packages")
		single_max_nums = int(settings.get("single_max_nums"))
		for name in dirs:
			if name in ignored_packages:
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
			try:
				jsonData = json.loads(content)
			except (ValueError):
				continue

			if not isinstance(jsonData, list):
				continue
			i = 0
			for item in jsonData:
				#only show 3 items if num max than 3
				if single_max_nums > 0 and i >= single_max_nums :
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
		for item in self.defaultCommand:
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
		#thanks wuliang
		self.view.run_command(item['command'], args)
		self.view.window().run_command(item['command'], args)
		sublime.run_command(item['command'], args)

	#check context condition
	def checkContext(self, plugin):
		return True
		if "context" not in plugin:
			return True
		if "window" in plugin and plugin["window"]:
			return True
		context = plugin["context"]
		name = plugin["name"]
		path = path = sublime.packages_path() + '/' + name + '/'
		import glob
		pyFiles = glob.glob("*.py")
		sublime.status_message(",".join(pyFiles))
		return True
