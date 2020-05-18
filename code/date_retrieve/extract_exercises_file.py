import time
import json
import bson
import re
from bson.json_util import dumps
from bson.objectid import ObjectId
from pathlib import Path

from utils import connect_to_db

"""
Script to extract exercise files submitted by students
"""


def extract_exercises(tasks_list=None):

	db, collection, fs = connect_to_db()

	# Get tasks from JSON
	with open('../data/input/missions_tasks.json', 'r') as file:
		missions = json.load(file)

	if tasks_list is None:
		tasks_list = []
		for mission_name, exercises in missions.items():
			for ex_id in exercises:
				ex_name, consider = exercises[ex_id]
				if consider == "Y":
					tasks_list.append({
						'mission_name': mission_name,
						'ex_id': ex_id,
						'ex_name': ex_name
					})

	# Make dir for all files
	path_all_files = '../../students_exercise_files/all_files/'
	Path(path_all_files).mkdir(parents=True, exist_ok=True)

	for num, task in enumerate(tasks_list):
		submissions = dumps(db.submissions.find(
			{
				'courseid': 'LINFO1101',
				'taskid': task['ex_name'],
				'grade': 100
			}
		))

		submissions_string_list = json.loads(submissions)

		students_files = {}

		for submission in submissions_string_list:
			username = submission['username'][0]
			input_id = ObjectId(submission['input']['$oid'])
			timestamp = submission['submitted_on']['$date']
			grade = submission['grade']

			if username not in students_files:
				students_files[username] = {'input': input_id, 'timestamp': timestamp, 'grade': grade}

			if students_files[username]['timestamp'] < timestamp:		# and students_files[username]['grade'] <= grade: # useless if only grade == 100
				students_files[username]['input'] = input_id
				students_files[username]['timestamp'] = timestamp
				students_files[username]['grade'] = grade

		print('{}/{} - {:20s} - Stud: {}'.format(num + 1, len(tasks_list), task['ex_name'], len(students_files)))

		for username, object in students_files.items():
			file_all_files = open(path_all_files + '/' + task['ex_name'] + '__' + username + '.py', 'w')

			input_dict = bson.BSON.decode(fs.get(object['input']).read())

			for key in sorted(input_dict):
				if key.startswith('@'):
					continue
				file = input_dict[key]
				file_no_comments = remove_comments(file)
				file_all_files.write(str(file_no_comments))

			file_all_files.close()


def remove_comments(file):
	file_no_comments = str(file)
	file_no_comments = re.sub(r'([\'\"])\1\1[\d\D]*?\1{3}', '', file_no_comments)
	result = re.search(r'([\'\"]).*#.*\1', file)
	if result is None:
		file_no_comments = re.sub(r'#.*', '', file_no_comments)

	return file_no_comments


if __name__ == '__main__':
	extract_exercises()
