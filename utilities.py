import json
from storage import *


#### Commands here should be moved inside the class and made async ####
#### These might cause problems in the long run
def createNewUserdata(author):
	print("Creating new user: "+str(author))


def checkIfUserExsists(id):
	if id in userdata:
		return True
	else:
		return False

