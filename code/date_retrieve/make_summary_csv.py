import json
import csv


def make_input_file():
	students = {}

	with open('../data/students_exam_results.json', 'r') as f:
		stud_exams = json.load(f)

	with open('../data/students_exercises_summary_results.json', 'r') as f:
		stud_exercises = json.load(f)

	print("Students Exam: {}".format(len(stud_exams)))
	print("Students Exercises: {}".format(len(stud_exercises)))

	for name in stud_exercises.keys():
		students[name] = {}
		students[name]['name'] = name
		if name in stud_exams:
			students[name]['passed'] = stud_exams[name]['is_passed']
			students[name]['grade'] = stud_exams[name]['grade']
			students[name]['session'] = stud_exams[name]['session']
		else:
			students[name]['passed'] = 'No Attempts'
			students[name]['grade'] = '0'
			students[name]['session'] = 'None'
		students[name]['tot_100'] = stud_exercises[name]['tot_100']
		students[name]['tot_attempted'] = stud_exercises[name]['tot_attempted']
		students[name]['avg_attempts'] = stud_exercises[name]['avg_attempts']
		students[name]['avg_time_to_best_grade'] = stud_exercises[name]['avg_time_to_best_grade']
		students[name]['avg_days_since_beginning'] = stud_exercises[name]['avg_days_since_beginning']

	print("Students: {}".format(len(students)))

	with open('../data/summary.csv', 'w') as fp:
		file_writer = csv.writer(fp, delimiter=',')

		values = list(students.values())
		columns = []

		for task, _ in values[0].items():
			columns.append(task)

		file_writer.writerow(columns)

		for student in values:
			file_writer.writerow(list(student.values()))


if __name__ == '__main__':
	make_input_file()
