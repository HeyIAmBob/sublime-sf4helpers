import sublime, sublime_plugin, subprocess, os, re

#Global Classes
class Symfony4Helper:
	def __init__(self, window, command):
		self.command = command
		self.window = window

	def getRootPath(self):
		if len(self.window.folders()) > 0:
			for folder in self.window.folders():
				print(os.path.join(folder, "bin", "console"))
				if os.path.exists(os.path.join(folder, "bin", "console")):
					return folder
					break
			sublime.message_dialog("No bin/console detected in the available root folder(s)")
		else:
			sublime.message_dialog("No folder open in this window")
		return None
		


	def run(self, command, console=True):
		rootFolder = self.getRootPath()
		if rootFolder:
			commandStr = ""
			if console :
				commandStr += "bin/console "
			commandStr += command
			print("Exec : " + commandStr)
			p = subprocess.Popen(commandStr, cwd=rootFolder, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			return p.communicate()[0]
		else:
			return None


	def runInternal(self, console=True):
		out = self.run(self.command, console)
		sublime.message_dialog(out.decode("utf-8"))
		return out.decode("utf-8")

	def runInternalAndReturn(self, console=True):
		out = self.run(self.command, console)
		if out:
			return out.decode("utf-8")
		return None
		

	def runExternal(self, sf4console=True):
		if sf4console:
			rootFolder = self.getRootPath()
			if rootFolder:
				commandStr = ""
				if sf4console :
					commandStr += "bin/console "
				commandStr += self.command
				p = subprocess.Popen("osascript -e 'tell app \"Terminal\" to activate' -e 'tell app \"Terminal\" to do script \"cd " + rootFolder + "\n" + commandStr + "\"'", cwd=rootFolder, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		else:
			if len(self.window.folders()) > 0:
				rootFolder = self.window.folders()[0]
				p = subprocess.Popen("osascript -e 'tell app \"Terminal\" to activate' -e 'tell app \"Terminal\" to do script \"cd " + rootFolder + "\n" + commandStr + "\"'", cwd=rootFolder, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			else:
				sublime.message_dialog("No folder open in this window")



class sf4hInternalCommand(sublime_plugin.WindowCommand):
	def run(self, command):
		Symfony4Helper(self.window, command).runInternal()
		
class sf4hExternalCommand(sublime_plugin.WindowCommand):
	def run(self, command):
		Symfony4Helper(self.window, command).runExternal()

class sf4hInternalAndDisplayCommand(sublime_plugin.WindowCommand):
	def run(self, command):
		about = Symfony4Helper(self.window, command).runInternalAndReturn()
		if about:
			self.window.new_file().run_command("insert",{"characters": about})

class sf4hPrompt(sublime_plugin.WindowCommand):
	def run(self, command, prompt):
		self.command = command
		self.window.show_input_panel(prompt, "", self.onPromptSet, None, None)
	def onPromptSet(self, text):
		print("parent class function. Need to be overwrited")

class sf4hPromptInternalCommand(sf4hPrompt):
	def onPromptSet(self, text):
		Symfony4Helper(self.window, self.command + " " + text).runInternal()

class sf4hPromptExternalCommand(sf4hPrompt):
	def onPromptSet(self, text):
		Symfony4Helper(self.window, self.command + " " + text).runExternal()

class sf4hPromptInternalAndDisplayCommand(sf4hPrompt):
	def onPromptSet(self, text):
		about = Symfony4Helper(self.window, self.command + " " + text).runInternalAndReturn()
		if about:
			self.window.new_file().run_command("insert",{"characters": about})

class sf4hPromptExternalCustomCommand(sf4hPrompt):
	def onPromptSet(self, text):
		Symfony4Helper(self.window, self.command + " " + text).runExternal(False)

#Specific calls
class sf4hPromptMake(sf4hPrompt):
	def onPromptSet(self, text):
		self.window.status_message("Executing command...")
		out = Symfony4Helper(self.window, self.command + " " + text).runInternal()
		files = re.search('created: (src/.*\.php)', out, re.IGNORECASE)
		if files:
			path = files.group(1)
			self.window.open_file(os.path.join(self.window.folders()[0], path))
