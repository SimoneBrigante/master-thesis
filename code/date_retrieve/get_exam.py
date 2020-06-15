import time
import json
import csv
import sys
from bson.json_util import dumps

from utils import connect_to_db


class StudentExam:

	def __init__(self, username, session, tasks_grade):
		self.username = username
		self.session = session
		self.tasks_grade = tasks_grade
		self.tasks_best_grade = {}
		self.tasks_best_grade_timestamp = {}
		self.tasks_attempt = {}
		for task in self.tasks_grade:
			self.tasks_best_grade[task] = 0
			self.tasks_best_grade_timestamp[task] = sys.maxsize
			self.tasks_attempt[task] = 0

	def new_attempt(self, task, grade, timestamp):
		if grade > self.tasks_best_grade[task]:
			self.tasks_best_grade[task] = grade
			self.tasks_best_grade_timestamp[task] = timestamp
		if grade == self.tasks_best_grade[task]:
			if timestamp < self.tasks_best_grade_timestamp[task]:
				self.tasks_best_grade_timestamp[task] = timestamp
		self.tasks_attempt[task] += 1

	def get_final_grade(self):
		final_grade = 0
		for task, points in self.tasks_grade.items():
			# print("Task: {} - Points: {}".format(task, points))
			final_grade += self.tasks_best_grade[task] * points

		return final_grade / 100

	def is_passed(self):
		return self.get_final_grade() >= 10

	def __str__(self):
		s = "{0:.<15s}[{1:2.0f}]:".format(self.username, self.get_final_grade())
		for task in self.tasks_grade:
			s += " {0}: {1:3.0f} ({2:3d})".format(task, self.tasks_best_grade[task], self.tasks_attempt[task])
		return s


def make_json(students):
	dictionary = {}

	for username, student in students:
		# print("{:20s}: avg_best_grade - {:.3f} - {}".format(username, student.get_final_grade(), student.session))
		dictionary[username] = {
			'session': student.session,
			'is_passed': student.is_passed(),
			'grade': float('{:.1f}'.format(student.get_final_grade()))
		}

	with open('../data/results/students_all_exams_results.json', 'w') as fp:
		json.dump(dictionary, fp, indent=4)


def get_students_for_exam():
	# print(" # Connection to database...")
	db, collection, fs = connect_to_db()
	# print(" # Database connected")

	with open('../data/input/exams_tasks_grades.json', 'r') as file:
		exams_tasks_grades = json.load(file)

	students = {}

	stud_exams = {}

	for exam, tasks in exams_tasks_grades.items():
		submissions = dumps(db.submissions.find({'courseid': exam}))

		submissions_string_list = json.loads(submissions)

		count_new = 0
		count_update = 0

		# print(" # Begin to process submissions... (%d)" % len(submissions_string_list))
		process_submissions_start = time.time()
		for submission in submissions_string_list:
			username = submission['username'][0]
			task_id = submission['taskid']
			grade = submission['grade']
			submitted_on = submission['submitted_on']['$date']

			if tasks[task_id] == 0:
				continue

			if username not in students:
				students[username] = StudentExam(username, exam, tasks)
				stud_exams[username] = {exam: StudentExam(username, exam, tasks)}
				count_new += 1
			elif students[username].session != exam:
				#print("\t{:20s} : {}".format(username, students[username].get_final_grade()))
				students[username] = StudentExam(username, exam, tasks)
				stud_exams[username][exam] = StudentExam(username, exam, tasks)
				count_update += 1

			(students[username]).new_attempt(task_id, grade, submitted_on)
			(stud_exams[username][exam]).new_attempt(task_id, grade, submitted_on)

		# Count Passed
		count_passed = 0
		for username, student in students.items():
			if student.is_passed():
				count_passed += 1

		print("{:20s} New: {:3d} - Updated: {:3d} - Passed: {:3d}/{:3d} ({:.2f})".format(exam, count_new, count_update, count_passed, len(students), count_passed/len(students)))

	print("\nStudents with more than one session:")
	for username, exams in stud_exams.items():
		if len(exams) > 1:
			print("{:20s}".format(username), end=" ")
			for exam, stud in exams.items():
				print("{:10s}: {:.1f}\t".format(exam, stud.get_final_grade()), end=" ")
			print("")

	print("Tot Students: %d" % (len(students)))
	sorted_students = sorted(students.items(), key=lambda kv: (kv[1]).get_final_grade(), reverse=True)

	return sorted_students


if __name__ == '__main__':

	sorted_students = get_students_for_exam()

	make_json(sorted_students)

	for name, obj in sorted_students:
		# print(obj)
		pass
