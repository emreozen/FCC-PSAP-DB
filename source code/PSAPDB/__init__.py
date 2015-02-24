import os
from flask import Flask
from flask.ext.mongokit import MongoKit, Document
from fccDatabase import UserModel, PsapModel, HistoryModel

import sys
import pymongo
from pymongo import MongoClient
import json
from geocodio import GeocodioClient

app = Flask(__name__)


## all initializations take place here

MONGO_URL= 'mongodb://heroku_app31976857:9joh54prcr94jg33hhpe5r7j0a@ds053130.mongolab.com:53130/heroku_app31976857'

GEOAPIKEY = '9925944c3c88f8de85ca505cc1994599c33885e'

geoClient = GeocodioClient(GEOAPIKEY)

from mongoSetup import mongoLabKit
kit = mongoLabKit(MONGO_URL)
kit.setLive(MONGO_URL)
#CRM databases
FCCDB = MongoKit(app)
FCCDB.register([UserModel])
FCCDB.register([PsapModel])
FCCDB.register([HistoryModel])

app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'top_secret_key'



import PSAPDB.views
import PSAPDB.fccDatabase
