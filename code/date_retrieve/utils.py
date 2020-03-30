import pymongo as pym
import gridfs


def connect_to_db():
	client = pym.MongoClient()
	db = client.INGInious
	collection = db.submissions
	fs = gridfs.GridFS(db)
	return db, collection, fs
