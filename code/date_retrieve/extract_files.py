import time
import os
import json
import bson
from bson.json_util import dumps
from bson.objectid import ObjectId

from utils import connect_to_db


def make_exercises_corpus(tasks_list=[]):
	db, collection, fs = connect_to_db()

	# Get tasks from JSON
	with open('../data/missions_tasks.json', 'r') as file:
		missions = json.load(file)

	if not tasks_list:
		for mission, tasks in missions.items():
			tasks_list.extend(tasks)

	for task in tasks_list:

		submissions = dumps(db.submissions.find(
			{
				'courseid': 'LINFO1101',
				'taskid': task,
				'grade': 100
			}
		))

		print(task)

		submissions_string_list = json.loads(submissions)

		students_files = {}

		for submission in submissions_string_list:
			username = submission['username'][0]
			input_id = ObjectId(submission['input']['$oid'])
			timestamp = submission['submitted_on']['$date']

			if username not in students_files:
				students_files[username] = {'input': input_id, 'timestamp': timestamp}
			if students_files[username]['timestamp'] > timestamp:
				students_files[username]['input'] = input_id
				students_files[username]['timestamp'] = timestamp

		f = open('../corpus/' + task + '.py', 'w+')
		for username, object in students_files.items():
			input_dict = bson.BSON.decode(fs.get(object['input']).read())
			f.write('"""\n')
			f.write(username + '\n')
			f.write('"""\n')

			for key in sorted(input_dict):
				if key.startswith('@'):
					continue

				f.write('# ' + str(key) + '\n')

				if type(input_dict[key]) is dict:
					file = input_dict[key]['value'].decode('ISO-8859-1')
				else:
					file = input_dict[key]

				f.write(str(file) + '\n\n')

		f.close()


if __name__ == '__main__':
	make_exercises_corpus()

