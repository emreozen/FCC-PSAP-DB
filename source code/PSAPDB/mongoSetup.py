from PSAPDB import app

class mongoLabKit(object):
	
	def __init__(self, URL):
		self.MONGO_URL = URL
	
	def setLocal(self):
		app.config['MONGODB_DATABASE'] = 'flask'
		app.config['MONGODB_HOST'] = 'localhost' 
		app.config['MONGODB_PORT'] = 27017
		app.config['MONGODB_USERNAME'] = None
		app.config['MONGODB_PASSWORD'] = None	
	
	def setLive(self, URL):
		self.MONGO_URL = URL
		app.config['MONGODB_DATABASE'] = 'heroku_app31976857'
		app.config['MONGODB_HOST'] = 'ds053130.mongolab.com:53130' 
		app.config['MONGODB_PORT'] = 53130
		app.config['MONGODB_USERNAME'] = 'heroku_app31976857'
		app.config['MONGODB_PASSWORD'] = '9joh54prcr94jg33hhpe5r7j0a'
		print 'MongoDB connection is Set'

