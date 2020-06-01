import os
import numpy as np
import shutil
import subprocess
import time
import json
import re
from pathlib import Path
from astminer_output_converter import convert_astminer_files
from pre_astminer_methods_substitution import pre_astminer_methods_substitution


class StringKeyReplacer:

	def __init__(self, code2vec_output_data_folder):
		method_keys_correspondences_path = code2vec_output_data_folder + '/' + dataset_name + '_method_keys_correspondences.json'
		method_keys_correspondences_fp = open(method_keys_correspondences_path, 'r')

		self.method_keys_correspondences = json.load(method_keys_correspondences_fp)

	def substitute_key_string(self, line, sub_type='TF'):
		key_string = line.split(' ')[0]

		if sub_type == 'TF':
			substitution = self.method_keys_correspondences[key_string]['exam_outcome']
		elif sub_type == 'method_name':
			substitution = self.method_keys_correspondences[key_string]['method_name']

		new_line = str(line).replace(key_string, substitution)
		return new_line


def execute_astminer(input_data_folder, code2vec_input_data_folder, dataset_name):
	cli_path = code2vec_input_data_folder + '/astminer-cli.jar'

	source = input_data_folder + '/' + dataset_name + '_keys_methods'
	destination = code2vec_input_data_folder + '/' + dataset_name + '/astminer_output'

	print('# Start astminer-cli.jar execution on ' + dataset_name + '...')
	start_time = time.time()
	subprocess.call(['java', '-jar', cli_path, 'code2vec', '--lang', 'py', '--project', source, '--output', destination])
	print('# End astminer-cli.jar execution on {} - Time: {}'.format(dataset_name, time.time() - start_time))


def merging_path_contexts(code2vec_input_data_folder, code2vec_output_data_folder, dataset_name):
	# Prepare Input
	input_path = code2vec_input_data_folder + '/' + dataset_name + '/astminer_output'

	list_of_files = [name for name in os.listdir(input_path) if name.startswith('path_contexts')]
	num_files = len(list_of_files)

	print('# Start merging path_contexts of {} - tot: {}'.format(dataset_name, num_files))
	start_time = time.time()

	# Prepare Output
	output_dir_path = code2vec_input_data_folder + '/' + dataset_name
	Path(output_dir_path).mkdir(parents=True, exist_ok=True)

	output_file_path = output_dir_path + '/' + dataset_name + '_merged.txt'

	fp = open(output_file_path, 'w')

	# File containing merged path_contexts
	for file_name in list_of_files:
		with open(input_path + '/' + file_name, 'r') as input_file:
			for line in input_file:
				fp.write(str(line))

	print('# End merging path_contexts of {} - Time: {}'.format(dataset_name, time.time() - start_time))


def split_path_contexts(code2vec_input_data_folder, code2vec_output_data_folder, dataset_name, val_ratio=0.1, test_ratio=0.1):
	output_file_dir = code2vec_input_data_folder

	datasets = [
		dataset_name + '_merged',
	]

	for dataset in datasets:
		input_file_path = code2vec_input_data_folder + '/' + dataset_name + '/' + dataset + '.txt'
		with open(input_file_path) as f:
			all_path_contexts = f.read().splitlines()

			np.random.shuffle(all_path_contexts)
			train_path_contexts, val_path_contexts, test_path_contexts = np.split(np.array(all_path_contexts),
																				  [int(len(all_path_contexts) * (1 - val_ratio - test_ratio)),
																				   int(len(all_path_contexts) * (1 - test_ratio))])

			print('Total files: ', len(all_path_contexts))
			print('Training: ', len(train_path_contexts))
			print('Validation: ', len(val_path_contexts))
			print('Testing: ', len(test_path_contexts))

			output_path = output_file_dir + '/' + dataset
			Path(output_path).mkdir(parents=True, exist_ok=True)

			string_replacer = StringKeyReplacer(code2vec_output_data_folder)

			with open(output_path + '/' + dataset + '.training.raw.txt', 'w') as f:
				for line in train_path_contexts:
					f.write('%s\n' % string_replacer.substitute_key_string(line))

			with open(output_path + '/' + dataset + '.validation.raw.txt', 'w') as f:
				for line in val_path_contexts:
					f.write('%s\n' % string_replacer.substitute_key_string(line))

			with open(output_path + '/' + dataset + '.test.raw.txt', 'w') as f:
				for line in test_path_contexts:
					f.write('%s\n' % line)


if __name__ == '__main__':
	input_data_folder = '../../students_exercise_files'
	code2vec_input_data_folder = '../../code2vec_input_data'
	code2vec_output_data_folder = '../../code2vec_output_data'
	# dataset_name = 'all_files'
	dataset_name = '0119_q1_all_grades'
	# exam_results_path = '../data/students_exam_results.json'
	exam_results_path = '../data/LINFO1101-0119__q1_results.json'

	pre_astminer_methods_substitution(input_data_folder, dataset_name, code2vec_output_data_folder, exam_results_path)

	execute_astminer(input_data_folder, code2vec_input_data_folder, dataset_name)

	merging_path_contexts(code2vec_input_data_folder, code2vec_output_data_folder, dataset_name)

	# conversion step
	convert_astminer_files(code2vec_input_data_folder, dataset_name)

	split_path_contexts(code2vec_input_data_folder, code2vec_output_data_folder, dataset_name)

