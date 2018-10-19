# creates tables for database stored in DB_FILE: blogs.db
# field names created; no records
import sqlite3   #enable control of an sqlite database

DB_FILE="blogs.db"

db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
c = db.cursor()               #facilitate db ops


def createTable(tableName, fieldNames):
	commandArgs = "("
	colTypes = []
	for name in fieldNames:
		commandArgs += name + " " + fieldNames[name] + ","
		colTypes.append(fieldNames[name])
	commandArgs = commandArgs[:-1]
	# print(colTypes)
	commandArgs += ")"
	# print ("CREATE TABLE " + tableName + " "+ commandArgs)
	c.execute("CREATE TABLE " + tableName + " "+ commandArgs)

def closeDB ():
	db.commit() #save changes
	db.close()  #close database

usersHeader = {"UserID":"INTEGER","PFP":"TEXT","Username":"TEXT", "Password":"TEXT"}
createTable("users", usersHeader)

postsHeader = {"PostID": "INTEGER", "BlogId": "INTEGER", "AuthorID": "INTEGER", "Content":"TEXT", "Timestamp":"DATETIME", "VOTES":"INTEGER"}
createTable( "posts", postsHeader)

blogsHeader = {"BlogID":"INTEGER PRIMARY KEY", "OwnerID":"INTEGER", "ColloboratorIDs":"TEXT","BlogName":"TEXT", "Category":"TEXT"}
createTable("blogs", blogsHeader)

closeDB()
