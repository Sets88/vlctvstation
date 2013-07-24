class MDict(object):
	def __init__(self, initials=None, accept_empty=False):
		if isinstance(initials, dict):
			if initials is None:
				self._initials = None
			else:
				self._initials = initials
			self._dict = {}
			self._accept_empty = accept_empty
	def __setitem__(self, key, value):
		if not value:
			if value != 0 and not self._accept_empty:
				return None
		if self._initials is not None:
			if key not in self._initials:
				return None
		if self._initials[key] == int:
			self._dict[key] = int(value)
		else:
			self._dict[key] = value


	def __getitem__(self, key):
		if key in self._dict:
			return self._dict[key]

	def __delitem__(self, key):
		return self._dict.pop(key)

	def __iter__(self):
		for item in self._dict.items():
			yield item[1]

	def keys(self):
		return self._dict.keys()

	def update(self, items):
		try:
			dict(items)
		except:
			return None

		for item in items.items():
			self.__setitem__(item[0], item[1])


	def has_not_a_single_item(self, items):
		try:
			items = list(items)
		except:
			return False

		for item in items:
			if item in self._dict:
				return True
		return False