import os
import json

class Settings(object):

	def __init__(self):
		self._settings = self.get_settings()

	def __getitem__(self, key):
		if key in self._settings:
			return self._settings[key]

	def __setitem__(self, key, value):
		self._settings[key] = value

	def __iter__(self):
		for item in self._settings.items():
			yield item[1]
	
	def keys(self):
		return self._settings.keys()

	def get_settings(self):
		settings = None
		currdir = os.path.dirname(os.path.abspath(__file__))
		if os.path.exists(os.path.expanduser("~/.vlctvstation.cfg")):
			try:
				file = open(os.path.expanduser("~/.vlctvstation.cfg"))
				settings = json.load(file)
			except:
				file = open(os.path.join(currdir, "default.cfg"))
				settings = json.load(file)
			return settings
		else:
			return json.load(open(os.path.join(currdir, "default.cfg")))

