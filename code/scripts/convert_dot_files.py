import csv
import os
import subprocess
from pathlib import Path
from graphviz import render


def import_description_csv_dictionary(path):
	description_dictionary = {}
	with open(path, 'r') as csv_file:
		csv_reader = csv.reader(csv_file)
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				print('Column names in description are {}'.format(', '.join(row)))
			else:
				dot_file, file_name, node_id, token, type = row
				file_name = file_name.split('/')[-1]
				node_id = int(node_id)
				type = type.split('|')[-1]

				if dot_file not in description_dictionary:
					description_dictionary[dot_file] = {
						'file_name': file_name,
						'nodes': {}
					}
				description_dictionary[dot_file]['nodes'][node_id] = (token, type)
			line_count += 1
		print('Processed {} lines in description'.format(line_count))

	return description_dictionary


def convert_dot_file(dot_files_folder, dot_file, description_dictionary, output_dir):
	input_fp = open(dot_files_folder + dot_file, 'r')
	output_fp = open(output_dir + dot_file, 'w')

	nodes = description_dictionary[dot_file]['nodes']

	for line in input_fp:
		if line != '}\n':
			line = line.replace('--', '->')
			output_fp.write(line)

	for node_id, tup in nodes.items():
		token, type = tup
		if token == 'null':
			output_fp.write('{} [label="({})"];\n'.format(node_id, type))
		else:
			output_fp.write('{} [label="{}\\n({})"];\n'.format(node_id, token, type))

	output_fp.write('}')
	output_fp.close()


def make_svg_files():
	pass


if __name__ == '__main__':
	folder = '../../code2vec_input_data/'
	datasets = [
		# '0119_q1',
		# '0119_q2',
		# '0119_q3',
		# '0119_q4',
		'exercises_q1',
		'exercises_q2',
		'exercises_q3',
		'exercises_q4',
	]

	for dataset_name in datasets:
		description_csv_path = folder + dataset_name + '/DOT/py/description.csv'
		dot_files_folder = folder + dataset_name + '/DOT/py/asts/'
		output_dir = folder + dataset_name + '/DOT/converted/'
		Path(output_dir).mkdir(parents=True, exist_ok=True)

		description_dictionary = import_description_csv_dictionary(description_csv_path)
		dot_files_list = [name for name in os.listdir(dot_files_folder) if name.startswith('ast_')]

		for dot_file in dot_files_list:
			convert_dot_file(dot_files_folder, dot_file, description_dictionary, output_dir)
