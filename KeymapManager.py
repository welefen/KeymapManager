import sublime, sublime_plugin
import os
import json

settings = sublime.load_settings("KeymapManager.sublime-settings")

class KeymapManagerCommand(sublime_plugin.TextCommand):
	"""
	keymap manager for plugins
	"""
	osname = sublime.platform()
	ctrlname = "ctrl"
	#ctrlname is cmd on macos
	if osname.lower() == "osx":
		ctrlname = "cmd"
	#add some default very usefull commands
	defaultCommand = [
		{"name": "Goto Anything...", "keys": [ctrlname + "+p"], "command": "show_overlay", "args": {"overlay": "goto", "show_files": True} },
		{"name": "Command Palette", "keys": [ctrlname + "+shift+p"], "command": "show_overlay", "args": {"overlay": "command_palette"} },
		{"name": "Goto Symbol...", "keys": [ctrlname + "+r"], "command": "show_overlay", "args": {"overlay": "goto", "text": "@"} },
		{"name": "Goto Line...",  "keys": [ctrlname + "+g"], "command": "show_overlay", "args": {"overlay": "goto", "text": ":"} },
		{"name": "Search Keywords", "keys": [ctrlname + "+;"], "command": "show_overlay", "args": {"overlay": "goto", "text": "#"} },
		{"name": "Show Console",  "keys": [ctrlname + "+`"],  "command": "show_panel", "args": {"panel": "console", "toggle": True} }
	]
	#installed plugins list
	plugins = None

	plugins_keys = None

	def run(self, edit):
		self.defaultCommand.sort(key=lambda x: x["name"].lower())
		
		if self.plugins == None:
			self.plugins = []
		if self.plugins_keys == None:
			self.plugins_keys = {}
		path = sublime.packages_path()
		dirs = os.listdir(path)
		#sort with insensitive
		dirs.sort(key=lambda x: x.lower())
		plugins = []
		ignored_packages = settings.get("ignored_packages") or []
		single_max_nums = int(settings.get("single_max_nums") or 3)
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
				if "keys" not in item or "command" not in item:
					continue
				if single_max_nums <= 0 or i <= single_max_nums :
					keys = item["keys"]
					if not isinstance(keys, list):
						keys = [keys]
					for key in keys:
						if key not in self.plugins_keys:
							self.plugins_keys[key] = []
						if item["command"] not in self.plugins_keys[key]:
							self.plugins_keys[key].append(item["command"])

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

		plugins.append(["KeymapConflict", "check plugins keymap conflict"])
		self.plugins.append({"name": "KeymapConflict"})

		self.view.window().show_quick_panel(plugins, self.panel_done)

	#panel done
	def panel_done(self, picked):
		if picked == -1:
			return 
		item = self.plugins[picked]
		if item["name"] == "KeymapConflict":
			self.checkKeymapConflict()
			return
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

	def checkKeymapConflict(self):
		keymapConflict=[]
		for key,item in self.plugins_keys.items():
			if len(item) > 1:
				keymapConflict.append([key, "Conflict in \""+", ".join(item) + "\" commands"])
		if len(keymapConflict) > 0:
			self.view.window().show_quick_panel(keymapConflict, self.check_panel_done)

	def check_panel_done(self, picked):
		pass