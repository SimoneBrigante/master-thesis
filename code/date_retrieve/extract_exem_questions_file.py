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


def extract_exercises(folder_name, tasks_list=None):

	db, collection, fs = connect_to_db()

	# Get tasks from JSON
	with open('../data/input/exams_tasks_grades.json', 'r') as file:
		exam_sessions = json.load(file)

	if tasks_list is None:
		tasks_list = []
		for exam_session, questions in exam_sessions.items():
			for question_id, question_score in questions.items():
				tasks_list.append({
					'exam_session': exam_session,
					'question_id': question_id,
					'question_score': question_score
				})

	# Make dir for all files
	path_all_files = '../../students_exercise_files/' + folder_name + '/'
	Path(path_all_files).mkdir(parents=True, exist_ok=True)

	count_good = 0
	count_bad = 0

	for num, task in enumerate(tasks_list):
		submissions = dumps(db.submissions.find(
			{
				'courseid': task['exam_session'],
				'taskid': task['question_id'],
				# 'grade': 100
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

		print('{}/{} - {:15s} {:10s} - Stud: {}'.format(num + 1, len(tasks_list), task['exam_session'], task['question_id'], len(students_files)))

		for username, object in students_files.items():
			try:
				input_dict = bson.BSON.decode(fs.get(object['input']).read())

				for key in sorted(input_dict):
					if key.startswith('test') or key.startswith('@'):
						continue
					file_all_files = open(path_all_files + '/' + task['exam_session'] + '_' + key + '__' + username + '.py', 'w')

					file = input_dict[key]
					file_no_comments = remove_comments(file)
					file_like_method = add_method_declaration_and_indentation(file_no_comments, task['question_id'])
					file_all_files.write(str(file_like_method))

					file_all_files.close()

				count_good += 1

			except:
				print('NO FILE - {:15s} {:10s} {:15s}'.format(task['exam_session'], task['question_id'], username))
				count_bad += 1

	print('Good: {} - Bad: {}'.format(count_good, count_bad))


def remove_comments(file):
	file_no_comments = str(file)
	file_no_comments = re.sub(r'([\'\"])\1\1[\d\D]*?\1{3}', '', file_no_comments)
	result = re.search(r'([\'\"]).*#.*\1', file)
	if result is None:
		file_no_comments = re.sub(r'#.*', '', file_no_comments)

	return file_no_comments


def add_method_declaration_and_indentation(file, question_id):
	new_file = 'def ' + question_id + '():\n'
	for line in file.split('\n'):
		new_file += '    ' + line + '\n'
	return new_file


if __name__ == '__main__':
	tasks_list = [
		{
			'exam_session': 'LINFO1101-0119',
			'question_id': 'q1',
		}
	]
	extract_exercises('0119_q1_all_grades', tasks_list)
