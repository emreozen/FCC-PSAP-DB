from flask import render_template, request, session, flash, redirect, url_for
from PSAPDB import app, FCCDB
from fccDatabase import UserModel, PsapModel
from functools import wraps
import pymongo
from mongokit import paginator
from geocodio import GeocodioClient
from PSAPDB import geoClient

###########
## FLASK functions for all the web pages
###########

@app.route('/')
@app.route('/index')
def index():

	return render_template('index.html')

def login_required(test): 
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs) 
		else:
			flash('You need to login first.')
			return redirect(url_for('login'))
	return wrap

@app.route('/login', methods=['GET', 'POST'])
def login(message=""):
	if 'message' in request.args:
		return render_template('login.html', target='verify', message=request.args['message'])
	return render_template('login.html', target='verify', message="")

@app.route('/verify', methods=['GET', 'POST'])
def verify():
	email = request.form['email']
	password = request.form['password']

	if not('email' in request.args) and ('password' in request.args):
		return redirect(url_for('login', message='email or password missing'))

	if verify_password(email, password) == False:
		return redirect(url_for('login', message='email or password wrong'))

	user = FCCDB.UserModel.find({'email':email})
	fixedUser = fixCursor(user) 
	

	session['logged_in'] = True
	session['email'] = email
	session['read_access'] = fixedUser[0]['read_access']
	session['write_access'] = fixedUser[0]['write_access']
	session['subscription'] = fixedUser[0]['subscription']

	return redirect(url_for('main'))

def verify_password(username, password):
		user = FCCDB.UserModel.find_one({'email':unicode(username)});
		
		#hashed password for production

		if not user or not user.verifyPassSimp(password):
		#	if not user or not user.verify_password(password):
			return False 
		return True

@app.route('/main')
@login_required
def main():
	adminUser = False

	if ('all' in session['read_access'] ):
		adminUser = True

	return render_template('main.html', email=session['email'], adminUser=adminUser)

@app.route('/list', methods=['GET'])
@login_required
def  list():
	email=session['email']

	dataList = 0;
	counter = 0
	adminUser = False

	if ('all' in session['read_access'] ):
		dataList = FCCDB.PsapModel.find()
		counter = FCCDB.PsapModel.find().count()
		adminUser = True
	else:
		dataList = FCCDB.PsapModel.find({'PSAP ID':{'$in': [int(i) for i in session['read_access']]}})
		counter = FCCDB.PsapModel.find({'PSAP ID':{'$in': [int(i) for i in session['read_access']]}}).count()

	dataListSorted = dataList.sort('PSAP ID', pymongo.ASCENDING)

	if ((( int(request.args['page'])-1)* 10) > int(counter) ):
		return page_not_found('500')
	pageSource = paginator.Paginator(dataListSorted, request.args['page'], 10)

	return render_template('list.html', dataList= fixCursor(dataListSorted), email = email, pgSource=pageSource, adminUser=adminUser)


@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	session.pop('email', None)
	session.pop('read_access', None)
	session.pop('write_access', None)
	return redirect(url_for('index'))

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(500)
def page_not_found(error):
		return render_template('error.html', errorMessage = ('Error '+str(error)+': Sorry, that was a BAD request.'))

def error(error):
	return render_template('error.html', errorMessage=error)

@app.route('/delete', methods=['GET', 'DELETE'])
@login_required
def delete():

	email=session['email']
	temp = 0

	if ('psapid' in request.args):
		deleteNode = FCCDB.PsapModel.find({'PSAP ID':int(request.args['psapid'])})
		temp = deleteNode[0]
		deleteNode[0].delete()

	dataList = 0;
	counter = 0
	adminUser = False

	if ('all' in session['write_access'] ):
		dataList = FCCDB.PsapModel.find()
		counter = FCCDB.PsapModel.find().count()
		adminUser = True

	else:	
		dataList = FCCDB.PsapModel.find({'PSAP ID':{'$in': [int(i) for i in session['write_access']]}})
		counter = FCCDB.PsapModel.find({'PSAP ID':{'$in': [int(i) for i in session['write_access']]}}).count()

	dataListSorted = dataList.sort('PSAP ID', pymongo.ASCENDING)
	
	if ((( int(request.args['page'])-1)* 10) > int(counter) ):
		return page_not_found('500')
	
	pageSource = paginator.Paginator(dataListSorted, request.args['page'], 10)

	return render_template('delete.html', dataList= fixCursor(dataListSorted), email = email, pgSource=pageSource, deleted=temp, adminUser=adminUser)

@app.route('/modify', methods=['GET', 'PUT'])
@login_required
def modify():
	f = 0
	v1 = 0
	v2 = 0
	psapHolder = 0
	if ('psapid' in request.args):
		# modifyNode = FCCDB.PsapModel.find({'PSAP ID':int(request.args['psapid'])})
		modifyNode = FCCDB.PsapModel.find_one({'PSAP ID':int(request.args['psapid'])})
		psapHolder = request.args['psapid']
		# temp = modifyNode[0]

		if 'pName' in request.args:
			v1 = modifyNode['PSAP Name']
			v2 = unicode(request.args['pName'])
			modifyNode['PSAP Name'] = unicode(request.args['pName'])
			modifyNode.save()
			f = 'PSAP Name'
		if 'state' in request.args:
			v1 = modifyNode['State']
			v2 = unicode(request.args['state'])			
			modifyNode['State'] = unicode(request.args['state'])
			f = 'State'
			modifyNode.save()
		if 'county' in request.args:
			v1 = modifyNode['County']
			v2 = unicode(request.args['county'])			
			modifyNode['County'] = request.args['county']
			f = 'County'
			modifyNode.save()
		if 'city' in request.args:
			v1 = modifyNode['City']
			v2 = unicode(request.args['city'])			
			modifyNode['City'] = request.args['city']
			f = 'City'
			modifyNode.save()
		if 'toc' in request.args:
			v1 = modifyNode['Type of Change']
			v2 = unicode(request.args['toc'])
			modifyNode['Type of Change'] = request.args['toc']
			f = 'Type of Change'
			modifyNode.save()
		if 'comments' in request.args:
			v1 = modifyNode['Comments']
			v2 = unicode(request.args['comments'])
			modifyNode['Comments'] = request.args['comments']
			f = 'Comments'
			modifyNode.save()
		if 'text2911' in request.args:
			v1 = modifyNode['Text to 911']
			v2 = unicode(request.args['text2911'])
			modifyNode['Text to 911'] = request.args['text2911']
			f = 'Text to 911'
			modifyNode.save()
		if 'psapcontact' in request.args:
			v1 = modifyNode['PSAP Contact']
			v2 = unicode(request.args['psapcontact'])
			modifyNode['PSAP Contact'] = request.args['psapcontact']
			f = 'PSAP Contact'
			modifyNode.save()
	dataList = 0;
	counter = 0
	adminUser = False

	if ('all' in session['write_access'] ):
		dataList = FCCDB.PsapModel.find()
		counter = FCCDB.PsapModel.find().count()
		adminUser = True
	else:	
		dataList = FCCDB.PsapModel.find({'PSAP ID':{'$in': [int(i) for i in session['write_access']]}})
		counter = FCCDB.PsapModel.find({'PSAP ID':{'$in': [int(i) for i in session['write_access']]}}).count()

	dataListSorted = dataList.sort('PSAP ID', pymongo.ASCENDING)

	if ((( int(request.args['page'])-1)* 10) > int(counter) ):
		return page_not_found('500')
	
	pageSource = paginator.Paginator(dataListSorted, request.args['page'], 10)

	return render_template('modify.html', dataList= fixCursor(dataListSorted), email = session['email'], pgSource=pageSource, cItem=f, v1=v1, v2=v2, psapidNum=psapHolder, adminUser=adminUser)


@app.route('/search', methods=['GET'])
@login_required
def search():

	email=session['email']
	search = False
	temp = 0

	dataList = 0;
	counter = 0
	adminUser = False
	searchResult = False
	searchQuery=''
	f =''

	dataList = FCCDB.PsapModel.find()
	counter = FCCDB.PsapModel.find().count()

	if ('all' in session['write_access'] ):
		adminUser = True

	if ('psapid' in request.args):
		dataList = FCCDB.PsapModel.find({'PSAP ID':int(request.args['psapid'])})
		counter = FCCDB.PsapModel.find({'PSAP ID':int(request.args['psapid'])}).count()
		f = 'PSAP ID'
		searchResult = True
		searchQuery = request.args['psapid']

	if ('psapname' in request.args):
		dataList = FCCDB.PsapModel.find({'PSAP Name':unicode(request.args['psapname'])})
		counter = FCCDB.PsapModel.find({'PSAP Name':unicode(request.args['psapname'])}).count()
		f = 'PSAP Name'
		searchResult = True
		searchQuery = request.args['psapname']

	if ('state' in request.args):
		dataList = FCCDB.PsapModel.find({'State':unicode(request.args['state'])})
		counter = FCCDB.PsapModel.find({'State':unicode(request.args['state'])}).count()
		f = 'State'
		searchResult = True
		searchQuery = request.args['state']

	if ('county' in request.args):
		dataList = FCCDB.PsapModel.find({'County':unicode(request.args['county'])})
		counter = FCCDB.PsapModel.find({'County':unicode(request.args['county'])}).count()
		f = 'County'
		searchResult = True
		searchQuery = request.args['county']

	if ('city' in request.args):
		dataList = FCCDB.PsapModel.find({'City':unicode(request.args['city'])})
		counter = FCCDB.PsapModel.find({'City':unicode(request.args['city'])}).count()
		f = 'City'
		searchResult = True
		searchQuery = request.args['city']

	if ('toc' in request.args):
		dataList = FCCDB.PsapModel.find({'Type of Change':unicode(request.args['toc'])})
		counter = FCCDB.PsapModel.find({'Type of Change':unicode(request.args['toc'])}).count()
		f = 'Type of Change'
		searchResult = True
		searchQuery = request.args['toc']

	if ('comments' in request.args):
		dataList = FCCDB.PsapModel.find({'Comments':unicode(request.args['comments'])})
		counter = FCCDB.PsapModel.find({'Comments':unicode(request.args['comments'])}).count()
		f = 'Comments'
		searchResult = True
		searchQuery = request.args['comments']

	if ('text2911' in request.args):
		dataList = FCCDB.PsapModel.find({'Text to 911':unicode(request.args['text2911'])})
		counter = FCCDB.PsapModel.find({'Text to 911':unicode(request.args['text2911'])}).count()
		f = 'Text to 911'
		searchResult = True
		searchQuery = request.args['text2911']

	if ('psapcontact' in request.args):
		dataList = FCCDB.PsapModel.find({'PSAP Contact':unicode(request.args['psapcontact'])})
		counter = FCCDB.PsapModel.find({'PSAP Contact':unicode(request.args['psapcontact'])}).count()
		f = 'PSAP Contact'
		searchResult = True
		searchQuery = request.args['psapcontact']


	dataListSorted = dataList.sort('PSAP ID', pymongo.ASCENDING)

	return render_template('search.html', dataList= fixCursor(dataListSorted), email = email, searchResult =searchResult, searchCategory=f, searchQuery=searchQuery, adminUser=adminUser, number= counter)

@app.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe():


	email=session['email']
	temp = 0
	subsNode = 0
	psapinfo = 0;
	

	if ('psapid' in request.args):
		subsNode = FCCDB.UserModel.find_one({'email':email})
		temp = subsNode
		subsNode.addSub('11')
		subsNode['subscription'].append(unicode('11'))
		subsNode.save()
		psapinfo=unicode(request.args['psapid'])

	dataList = 0;
	counter = 0
	adminUser = False

	if ('all' in session['read_access'] ):
		dataList = FCCDB.PsapModel.find()
		counter = FCCDB.PsapModel.find().count()
		adminUser = True

	else:	
		dataList = FCCDB.PsapModel.find({'PSAP ID':{'$in': [int(i) for i in session['read_access']]}})
		counter = FCCDB.PsapModel.find({'PSAP ID':{'$in': [int(i) for i in session['read_access']]}}).count()

	dataListSorted = dataList.sort('PSAP ID', pymongo.ASCENDING)

	if ((( int(request.args['page'])-1)* 10) > int(counter) ):
		return page_not_found('500')
	
	pageSource = paginator.Paginator(dataListSorted, request.args['page'], 10)

	return render_template('subscribe.html', dataList= fixCursor(dataListSorted), email = email, pgSource=pageSource, subscribed=temp, subscription=session['subscription'], subscribedNode=psapinfo, adminUser=adminUser)


@app.route('/addpsap', methods=['GET', 'POST'])
@login_required
def addpsap():

	dataList = 0;
	counter = 0
	adminUser = False
	added = 0

	if ('all' in session['read_access'] ):
		dataList = FCCDB.UserModel.find()
		counter = FCCDB.UserModel.find().count()
		adminUser = True

	if (request.form):

		newPsap = FCCDB.PsapModel()
		newPsap['PSAP ID'] = int(request.form['psapid'])
		newPsap['PSAP Name'] = request.form['psapname']
		newPsap['State'] = request.form['state']
		newPsap['County'] = request.form['county']
		newPsap['City'] = request.form['city']
		newPsap['Type of Change'] = request.form['toc']
		newPsap['Comments'] = request.form['comments']
		newPsap['Text to 911'] = request.form['text2911']
		newPsap['PSAP Contact'] = request.form['psapcontact']
		newPsap.save()
		added = request.form['psapid'] 

	return render_template('addpsap.html', adminUser= adminUser, added=added )


@app.route('/addUser', methods=['GET', 'POST'])
@login_required
def addUser():

	dataList = 0;
	counter = 0
	adminUser = False
	added = 0
	rd = []
	wd = []

	if ('all' in session['read_access'] ):
		dataList = FCCDB.UserModel.find()
		counter = FCCDB.UserModel.find().count()
		adminUser = True
	else:
		return error( "YOU ARE NOT AUTHORIZED FOR THIS PAGE")

	if (request.form):
		newUser = FCCDB.UserModel()
		newUser.email = request.form['email']
		#hash the password for production
		newUser.password = request.form['password']
		#newUser.password = hash_password(request.form['password'])

		rd.append(request.form['read_access'])
		wd.append(request.form['write_access'])
		newUser.read_access = rd
		newUser.write_access = wd
		newUser.save()
		added = request.form['email'] 

	return render_template('addUser.html', adminUser= adminUser, added=added )

@app.route('/listUser', methods=['GET'])
@login_required
def listUser():
	email=session['email']

	dataList = 0;
	counter = 0
	adminUser = False

	if ('all' in session['read_access'] ):
		dataList = FCCDB.UserModel.find()
		counter = FCCDB.UserModel.find().count()
		adminUser = True
	else:
		return error( "YOU ARE NOT AUTHORIZED FOR THIS PAGE")
	

	dataListSorted = dataList.sort('registered', pymongo.ASCENDING)

	if ((( int(request.args['page'])-1)* 10) > int(counter) ):
		return page_not_found('500')
	pageSource = paginator.Paginator(dataListSorted, request.args['page'], 10)

	return render_template('listUser.html', dataList= fixCursor(dataListSorted), email = email, pgSource=pageSource, adminUser=adminUser)


@app.route('/modifyUser', methods=['GET', 'POST'])
@login_required
def modifyUser():

	dataList = 0;
	counter = 0
	adminUser = False

	if ('all' in session['read_access'] ):
		dataList = FCCDB.UserModel.find()
		counter = FCCDB.UserModel.find().count()
		adminUser = True
	else:
		return error( "YOU ARE NOT AUTHORIZED FOR THIS PAGE")

	f = 0
	v1 = 0
	v2 = 0
	userHolder = 0
	if ('email' in request.args):
		modifyNode = FCCDB.UserModel.find_one({'email':unicode(request.args['email'])})
		userHolder = request.args['email']
		
		if 'read_access' in request.args:
			v1 = modifyNode['read_access']
			v2 = unicode(request.args['read_access'])

			modifyNode['read_access'] = unicode(request.args['read_access'])
			modifyNode.save()
			f = 'PSAP Name'

		if 'write_access' in request.args:
			v1 = modifyNode['write_access']
			v2 = unicode(request.args['write_access'])			
			modifyNode['write_access'] = unicode(request.args['write_access'])
			f = 'Write Access'
			modifyNode.save()


	dataList = FCCDB.UserModel.find()
	counter = FCCDB.UserModel.find().count()

	dataListSorted = dataList.sort('PSAP ID', pymongo.ASCENDING)

	if ((( int(request.args['page'])-1)* 10) > int(counter) ):
		return page_not_found('500')
	
	pageSource = paginator.Paginator(dataListSorted, request.args['page'], 10)

	return render_template('modifyUser.html', dataList= fixCursor(dataListSorted), email = session['email'], pgSource=pageSource, cItem=f, v1=v1, v2=v2, psapidNum=userHolder, adminUser=adminUser)

@app.route('/deleteUser', methods=['GET', 'DELETE'])
@login_required
def deleteUser():

	dataList = 0;
	counter = 0
	adminUser = False

	if ('all' in session['read_access'] ):
		dataList = FCCDB.UserModel.find()
		counter = FCCDB.UserModel.find().count()
		adminUser = True
	else:
		return error( "YOU ARE NOT AUTHORIZED FOR THIS PAGE")


	email=session['email']
	temp = 0

	if ('email' in request.args):
		deleteNode = FCCDB.UserModel.find({'email':unicode(request.args['email'])})
		temp = deleteNode[0]
		deleteNode[0].delete()

	else:	
		dataList = FCCDB.UserModel.find()
		counter = FCCDB.UserModel.find().count()

	dataListSorted = dataList.sort('PSAP ID', pymongo.ASCENDING)

	if ((( int(request.args['page'])-1)* 10) > int(counter) ):
		return page_not_found('500')
	
	pageSource = paginator.Paginator(dataListSorted, request.args['page'], 10)

	return render_template('deleteUser.html', dataList= fixCursor(dataListSorted), email = email, pgSource=pageSource, deleted=temp, adminUser=adminUser)

# geocoding function
def geoCode(county, city, state):

	address = str(county) + ' ' + str(city) + ' ' + str(state)
	geoLocation = geoClient.geocode(address)

	return geoLocation


# sort columns

def sortColumn(dataList, sortby):

	dataListSorted = dataList.sort(str(sortby, pymongo.ASCENDING)	)

	return dataListSorted


def fixCursor(data):
	jsonData = []
	for doc in data:
		jsonData.append(doc)	

	return jsonData