import yaml

class Config:
	def __init__(self, cdict):
		attrs = set(self.attrs) # copy and "unfreeze"
		for k, v in cdict.items():
			attrs.remove(k) # check if the key is allowed, mark it as present
			setattr(self, k, v)
		if len(attrs) != 0:
			raise KeyError('missing required bot config keys: %s' % attrs)

class WebConfig(Config):
	attrs = frozenset([
		'port',
		'host',
		'cookie_secret',
		'debug',
	])

__doc = yaml.load(open('config.yaml', 'r'))
web = WebConfig(__doc['web'])
