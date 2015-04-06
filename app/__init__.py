from flask import Flask
from getloc import GetLoc

gl = GetLoc()
app = Flask(__name__)

from app import views
