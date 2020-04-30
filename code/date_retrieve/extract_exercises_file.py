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

def make_exercises_corpus(tasks_list=None, change_method=False):

	db, collection, fs = connect_to_db()

	# Get tasks from JSON
	with open('../data/missions_tasks.json', 'r') as file:
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

	for num, task in enumerate(tasks_list):
		submissions = dumps(db.submissions.find(
			{
				'courseid': 'LINFO1101',
				'taskid': task['ex_name'],
				'grade': 100
			}
		))

		# Make dir for all files
		path_all_files = '../../files/all_files/all/'
		Path(path_all_files).mkdir(parents=True, exist_ok=True)
		path_all_files_TF = '../../files/all_files_TF/all/'
		Path(path_all_files_TF).mkdir(parents=True, exist_ok=True)

		submissions_string_list = json.loads(submissions)

		students_files = {}

		for submission in submissions_string_list:
			username = submission['username'][0]
			input_id = ObjectId(submission['input']['$oid'])
			timestamp = submission['submitted_on']['$date']
			grade = submission['grade']

			if username not in students_files:
				students_files[username] = {'input': input_id, 'timestamp': timestamp, 'grade': grade}

			if students_files[username]['timestamp'] > timestamp and students_files[username]['grade'] <= grade:
				students_files[username]['input'] = input_id
				students_files[username]['timestamp'] = timestamp
				students_files[username]['grade'] = grade

		print('{}/{} - {:20s} - Stud: {}'.format(num + 1, len(tasks_list), task['ex_name'], len(students_files)))

		for username, object in students_files.items():
			file_all_files = open(path_all_files + '/' + task['ex_name'] + '_' + username + '.py', 'w')
			file_all_files_TF = open(path_all_files_TF + '/' + task['ex_name'] + '_' + username + '.py', 'w')

			input_dict = bson.BSON.decode(fs.get(object['input']).read())

			for key in sorted(input_dict):
				if key.startswith('@'):
					continue

				if type(input_dict[key]) is dict:
					file = input_dict[key]['value'].decode('ISO-8859-1')
				else:
					file = input_dict[key]

				if change_method:
					file_TF = change_method_name(username, file)
					file_all_files_TF.write(file_TF)

				file_all_files.write(str(file))

			file_all_files.close()


def change_method_name(student, file):
	with open('../data/exam_TF.json', 'r') as exam_TF:
		student_outcome = json.load(exam_TF)
	if student not in student_outcome:
		label = 'NOTPASSED'
	else:
		if student_outcome[student]:
			label = 'PASSED'
		else:
			label = 'NOTPASSED'

	file = re.sub(r'def .*\(', 'def ' + str(label) + '(', file)

	return file


if __name__ == '__main__':
	make_exercises_corpus(change_method=True)

