import sys
import os
import re
import json
import unidecode

from pathlib import Path


class StringCounter:

	def __init__(self, counter_array=None):
		if counter_array is None:
			counter_array = [0, 0, 0, 0, 0]
		self.counter_array = counter_array
		self.len = len(self.counter_array)
		self.char_offset = 97

	def increase_counter(self):
		self.counter_array[0] += 1
		for i in range(self.len - 1):
			rest = self.counter_array[i] // 26
			self.counter_array[i] = self.counter_array[i] % 26
			if rest == 1:
				self.counter_array[i + 1] += 1
			else:
				break

	def get_next_string(self):
		self.increase_counter()
		return ''.join([chr(n + self.char_offset) for n in self.counter_array])


def pre_astminer_methods_substitution(input_data_folder, dataset_name, code2vec_output_data_folder):
	input_path = input_data_folder + '/' + dataset_name
	output_path = input_data_folder + '/' + dataset_name + '_keys_methods'

	# Create output directory
	Path(output_path).mkdir(parents=True, exist_ok=True)

	exam_TF_path = '../data/input/exam_TF.json'
	exam_TF_fp = open(exam_TF_path, 'r')
	output_file_path = code2vec_output_data_folder + '/method_keys_correspondences.json'

	# Dictonary to load info, will be converted into .json file
	method_keys_correspondences = {}
	students_outcome = json.load(exam_TF_fp)

	list_of_files = [name for name in os.listdir(input_path)]
	sc = StringCounter()

	for file_name in list_of_files:
		input_file = open(input_path + '/' + file_name, 'r')
		output_file = open(output_path + '/' + file_name, 'w')

		key_string = sc.get_next_string()

		# File as a string
		input_file_string = input_file.read()

		# Remove accents
		input_file_string_no_accents = unidecode.unidecode(input_file_string)

		# Extract useful information
		split = file_name[:-3].replace(" ", "").split('__')
		task_name, student_username = split
		re_search_result = re.search(r'def ([a-zA-Z0-9_\s]+)\(', input_file_string_no_accents)
		if re_search_result is None:
			# DISCARD FILE
			print('Discarding file: {}'.format(file_name))
			input_file.close()
			output_file.close()
			continue

		method_name = re_search_result.group(1)
		method_name = method_name.lower().strip()

		# Substitute method_name with key_string
		output_file_string = re.sub(r'def [a-zA-Z0-9_\s]+\(', 'def ' + key_string + '(', input_file_string_no_accents)
		# Write converted file
		output_file.write(output_file_string)

		# Handle cases where student hasn't done the exam
		# TODO: Separate cases NOT_PASSED and NOT_DONE?
		if student_username not in students_outcome:
			exam_outcome = 'notpassed'
		else:
			if students_outcome[student_username]:
				exam_outcome = 'passed'
			else:
				exam_outcome = 'notpassed'

		method_keys_correspondences[key_string] = {
			'method_name': method_name,
			'student': student_username,
			'task_name': task_name,
			'exam_outcome': exam_outcome
		}

		input_file.close()
		output_file.close()

	with open(output_file_path, 'w') as fp:
		json.dump(method_keys_correspondences, fp, indent=4)


if __name__ == '__main__':
	args = sys.argv
	input_data_folder = args[1]
	dataset_name = args[2]
	code2vec_output_data_folder = args[3]

	pre_astminer_methods_substitution(input_data_folder, dataset_name, code2vec_output_data_folder)
