import time
import json
import csv
import sys
from bson.json_util import dumps
from datetime import datetime

import utils

DATE_BEGIN_OF_SEMESTER = datetime(2018, 9, 17)


class StudentExercise:

	def __init__(self, username, tasks_list):
		self.username = username
		self.tasks = {}

		for task_name in tasks_list:
			self.tasks[task_name] = Task(task_name)

	def get_task(self, task_name):
		return self.tasks[task_name]

	def sum_of_grades(self):
		tot = 0
		for task_name, task in self.tasks.items():
			tot += task.best_grade
		return tot

	def __str__(self):
		s = "{}:\n".format(self.username)
		for task_name, task in self.tasks.items():
			s += "\t{0:.<25s} {1:3.0f} ({2:3d})\n".format(task_name, task.best_grade, task.attempts)
		return s


class Task:
	def __init__(self, task_name):
		self.task_name = task_name
		self.best_grade = 0
		self.best_grade_timestamp = sys.maxsize
		self.attempts = 0
		self.attempted = 0
		self.first_submission_timestamp = sys.maxsize
		self.days_since_beginning = 0

	def new_attempt(self, grade, timestamp):
		# Handle Best Grade and its timestamp
		if grade > self.best_grade:
			self.best_grade = grade
			self.best_grade_timestamp = timestamp
			self.update_days_since_beginning()
		if grade == self.best_grade:
			if timestamp < self.best_grade_timestamp:
				self.best_grade_timestamp = timestamp
				self.update_days_since_beginning()
		# Handle Time of First Submission
		if timestamp < self.first_submission_timestamp:
			self.first_submission_timestamp = timestamp
		self.attempts += 1
		self.attempted = 1

	def update_days_since_beginning(self):
		date_best_grade = datetime.fromtimestamp(self.best_grade_timestamp/1000)
		difference = date_best_grade - DATE_BEGIN_OF_SEMESTER
		self.days_since_beginning = difference.days


def make_json(students):
	dictionary = {}

	for username, student in students:
		dictionary[username] = make_summary_features(student)

		print("{:20s}: avg_best_grade - {:.3f}".format(username, dictionary[username]['avg_best_grade']))

		for task_name, task in student.tasks.items():
			dictionary[username][task_name + '_best_grade'] = task.best_grade
			dictionary[username][task_name + '_attempted'] = task.attempted
			dictionary[username][task_name + '_attempts'] = task.attempts
			dictionary[username][task_name + '_time_to_best_grade'] = int((task.best_grade_timestamp - task.first_submission_timestamp) / 1000)
			dictionary[username][task_name + '_days_since_beginning'] = task.days_since_beginning

	with open('../data/exercises.json', 'w') as fp:
		json.dump(dictionary, fp, indent=4)


def make_summary_features(student):
	dictionary = {}
	tot_tasks = len(student.tasks)
	tot_best_grade = 0
	tot_attempted = 0
	tot_attempts = 0
	tot_time_to_best_grade = 0
	tot_days_since_beginning = 0
	for task_name, task in student.tasks.items():
		tot_best_grade += task.best_grade
		tot_attempted += task.attempted
		tot_attempts += task.attempts
		tot_time_to_best_grade += int((task.best_grade_timestamp - task.first_submission_timestamp) / 1000)
		tot_days_since_beginning += task.days_since_beginning
	dictionary['avg_best_grade'] = tot_best_grade / tot_tasks
	dictionary['avg_attempted'] = tot_attempted / tot_tasks
	dictionary['avg_attempts'] = tot_attempts / tot_tasks
	dictionary['avg_time_to_best_grade'] = tot_time_to_best_grade / tot_tasks
	dictionary['avg_days_since_beginning'] = tot_days_since_beginning / tot_tasks

	return dictionary


def get_students_for_exercises(tasks_list=[]):
	# print(" # Connection to database...")
	db, collection, fs = utils.connect_to_db()
	# print(" # Database connected")

	# Get tasks from JSON
	with open('../data/missions_tasks.json', 'r') as file:
		missions = json.load(file)

	if not tasks_list:
		for mission, tasks in missions.items():
			tasks_list.extend(tasks)

	students = {}

	for task in tasks_list:

		submissions = dumps(db.submissions.find({'courseid': 'LINFO1101', 'taskid': task}))

		submissions_string_list = json.loads(submissions)

		for submission in submissions_string_list:
			username = submission['username'][0]
			task_id = submission['taskid']
			grade = submission['grade']
			submitted_on = submission['submitted_on']['$date']

			if username not in students:
				students[username] = StudentExercise(username, tasks_list)

			(students[username]).get_task(task_id).new_attempt(grade, submitted_on)

	print("Tot Students: %d" % (len(students)))
	sorted_students = sorted(students.items(), key=lambda kv: (kv[1]).sum_of_grades(), reverse=True)

	return sorted_students


if __name__ == '__main__':

	sorted_students = get_students_for_exercises()

	make_json(sorted_students)

	for name, student in sorted_students:
		# print(obj)
		pass

