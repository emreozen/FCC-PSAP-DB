from pymongo import Connection
from pymongo import collection
from pymongo import database
from flask.ext.mongokit import MongoKit, Document
from datetime import datetime
from bson.objectid import ObjectId
###########
## Database schemas for Users, PSAPs and Historical Informations
###########

class UserModel(Document):
	__collection__ = 'fccusers'
	__database__ = 'FCCDB'
	structure = {
		'email' : unicode,
		'password' : unicode,
		'read_access' : [unicode],
		'write_access':[unicode],
		'subscription':[unicode],
		'active': bool,
		'registered': datetime,
		}
	required_fields = ['email', 'password']
	default_values = {'registered' : datetime.utcnow, 'active': True}
	use_dot_notation = True

	def verifyPassSimp(self, password):
		if self.password == password and self.active == True:
			return True
		return False
	
	def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password_hash)

	def addSub(self, sub):
		self.subscription.append(unicode(sub))
		print "self-subs"
		print self.subscription


class PsapModel(Document):
	__collection__ = 'psapTable'
	__database__ = 'FCCDB'
	structure = {
		'PSAP ID' : int,
		'PSAP Name' : unicode,
		'State': unicode,
		'County': unicode,
		'City': unicode,
		'Type of Change': unicode,
		'Comments': unicode,
		'Text to 911':unicode,
		'PSAP Contact':unicode,  
		}
	required_fields = ['PSAP ID', 'PSAP Name', 'State', 'County', 'Type of Change']
	default_values = {'Text to 911' : ''}
	use_dot_notation = True

class HistoryModel(Document):
	__collection__ = 'historyTable'
	__database__ = 'FCCDB'
	structure = {
		'originalPSAP' : PsapModel,
		'updatedPSAP' : PsapModel,
		'changeTime': datetime,
		'changeUser': unicode,
		'changeType': unicode,

		}
	required_fields = ['changeUser', 'changeTime']
	default_values = {'changeTime' : datetime.utcnow}
	use_dot_notation = True
