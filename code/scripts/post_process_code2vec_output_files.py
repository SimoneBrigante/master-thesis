import json
import csv


def import_tokens_csv_dictionary(path):
	tokens_dictionary = {}
	with open(path, 'r') as csv_file:
		csv_reader = csv.reader(csv_file)
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				print('Column names in tokens are {}'.format(', '.join(row)))
			else:
				tokens_dictionary[int(row[0])] = row[1]
			line_count += 1
		print('Processed {} lines in tokens'.format(line_count))

	return tokens_dictionary


def import_path_csv_dictionary(path):
	paths_dictionary = {}
	with open(path, 'r') as csv_file:
		csv_reader = csv.reader(csv_file)
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				print('Column names in paths are {}'.format(', '.join(row)))
			else:
				paths_dictionary[int(row[0])] = row[1]
			line_count += 1
		print('Processed {} lines in paths'.format(line_count))

	return paths_dictionary


def post_process_code2vec_output_files(code2vec_input_data_folder, code2vec_output_data_folder, dataset_name):
	output_dictionary_path = code2vec_output_data_folder + dataset_name + '_test_all_output_dictionary.json'
	method_keys_correspondences_path = code2vec_output_data_folder + dataset_name + '_method_keys_correspondences.json'
	path_converted_path = code2vec_input_data_folder + dataset_name + '/astminer_output/paths_converted.csv'
	tokens_path = code2vec_input_data_folder + dataset_name + '/astminer_output/tokens.csv'

	with open(output_dictionary_path, 'r') as file:
		output_dictionary = json.load(file)

	with open(method_keys_correspondences_path, 'r') as file:
		method_keys_correspondences = json.load(file)

	path_converted = import_path_csv_dictionary(path_converted_path)
	tokens = import_tokens_csv_dictionary(tokens_path)

	for string_key in output_dictionary:
		output_dictionary[string_key]['student'] = method_keys_correspondences[string_key]['student']
		output_dictionary[string_key]['task_name'] = method_keys_correspondences[string_key]['task_name']
		output_dictionary[string_key]['method_name'] = method_keys_correspondences[string_key]['method_name']
		output_dictionary[string_key]['exam_outcome'] = method_keys_correspondences[string_key]['exam_outcome']
		for attention_obj in output_dictionary[string_key]['attentions']:
			if attention_obj['path'] == '<PAD_OR_OOV>' or attention_obj['token1'] == '<PAD_OR_OOV>' or attention_obj['token2'] == '<PAD_OR_OOV>':
				continue
			path_id = int(attention_obj['path'])
			token1_id = int(attention_obj['token1'])
			token2_id = int(attention_obj['token2'])

			attention_obj['path'] = path_converted[path_id]
			attention_obj['token1'] = tokens[token1_id]
			attention_obj['token2'] = tokens[token2_id]

	with open(code2vec_output_data_folder + dataset_name + '_final_dictionary.json', 'w') as fp:
		json.dump(output_dictionary, fp, indent=4)


if __name__ == '__main__':
	code2vec_input_data_folder = '../../code2vec_input_data/'
	code2vec_output_data_folder = '../../code2vec_output_data/'

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
		post_process_code2vec_output_files(code2vec_input_data_folder, code2vec_output_data_folder, dataset_name)
