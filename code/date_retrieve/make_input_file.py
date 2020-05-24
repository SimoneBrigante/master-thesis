import json
import csv


def make_input_file():
	students = {}

	with open('../data/students_exam_results.json', 'r') as f:
		stud_exam = json.load(f)

	with open('../data/exercises.json', 'r') as f:
		stud_exer = json.load(f)

	print("Students Exam: {}".format(len(stud_exam)))
	print("Students Exercises: {}".format(len(stud_exer)))

	for name in stud_exam.keys():
		if name in stud_exer:
			students[name] = stud_exer[name]
			students[name]['exam'] = int(stud_exam[name]['is_passed'])

	print("Students: {}".format(len(students)))

	with open('../data/input.csv', 'w') as fp:
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
