import csv
import sys


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


def import_node_types_csv_dictionary(path):
	node_types_dictionary = {}
	with open(path, 'r') as csv_file:
		csv_reader = csv.reader(csv_file)
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				print('Column names in node types are {}'.format(', '.join(row)))
			else:
				node_types_dictionary[int(row[0])] = (row[1].split('|'))[-1]
			line_count += 1
		print('Processed {} lines in node types'.format(line_count))

	return node_types_dictionary


def import_path_csv_dictionary(path):
	paths_dictionary = {}
	with open(path, 'r') as csv_file:
		csv_reader = csv.reader(csv_file)
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				print('Column names in paths are {}'.format(', '.join(row)))
			else:
				paths_dictionary[int(row[0])] = [int(n) for n in row[1].split(' ')]
			line_count += 1
		print('Processed {} lines in paths'.format(line_count))

	return paths_dictionary


def import_path_context_all_txt_list(path):
	path_context_list = []
	with open(path, 'r') as fp:
		line_count = 0
		for index, line in enumerate(fp):
			elements = line.split(' ')
			method_name = elements[0]
			path_context_list.append((method_name, []))
			for element in elements[1:]:
				path_context_list[index][1].append([int(n) for n in element.split(',')])
			line_count += 1
		print('Processed {} lines in context paths'.format(line_count))

	return path_context_list


def make_path_contexts_converted(path_context_list, tokens_dictionary):
	path_contexts_with_tokens = []
	for index, entry in enumerate(path_context_list):
		method_name, path_contexts = entry
		path_contexts_with_tokens.append((method_name, []))
		for triplet in path_contexts:
			path_contexts_with_tokens[index][1].append([
				tokens_dictionary[triplet[0]],
				triplet[1],
				tokens_dictionary[triplet[2]]
			])
	return path_contexts_with_tokens


def make_paths_converted(paths_dictionary, node_types_dictionary):
	paths_with_node_types_dictionary = {}
	for path, tokens in paths_dictionary.items():
		paths_with_node_types_dictionary[path] = []
		for token in tokens:
			paths_with_node_types_dictionary[path].append(node_types_dictionary[token])

	return paths_with_node_types_dictionary


def convert_astminer_files(code2vec_input_data_folder, dataset_name):
	path_tokens_csv = code2vec_input_data_folder + '/' + dataset_name + '/astminer_output/tokens.csv'
	path_node_types_csv = code2vec_input_data_folder + '/' + dataset_name + '/astminer_output/node_types.csv'
	path_paths_csv = code2vec_input_data_folder + '/' + dataset_name + '/astminer_output/paths.csv'
	merged_path_contexts_txt = code2vec_input_data_folder + '/' + dataset_name + '/' + dataset_name + '_merged.txt'

	destination_dir = code2vec_input_data_folder + '/' + dataset_name

	tokens_dictionary = import_tokens_csv_dictionary(path_tokens_csv)
	node_types_dictionary = import_node_types_csv_dictionary(path_node_types_csv)
	paths_dictionary = import_path_csv_dictionary(path_paths_csv)
	path_context_list = import_path_context_all_txt_list(merged_path_contexts_txt)

	# Replace tokens in path contexts
	path_contexts_with_tokens = make_path_contexts_converted(path_context_list, tokens_dictionary)

	# Replace node_type ids with 'meaningful' string in paths
	paths_with_node_types_dictionary = make_paths_converted(paths_dictionary, node_types_dictionary)

	"""
	with open(destination_dir + '/' + dataset_name + '_merged_converted.txt', 'w') as fp:
		for index, tup in enumerate(path_contexts_with_tokens):
			line = '' + tup[0] + ' '
			for triplet in tup[1]:
				line += ','.join(str(t) for t in triplet) + ' '
				fp.write(line)
				line = ''
			fp.write('\n')
	"""

	with open(destination_dir + '/paths_converted.csv', 'w') as fp:
		fp.write('id, path\n')
		"""
		for path_id, tokens_list in paths_with_node_types_dictionary.items():
			line = str(path_id) + ', '
			for index, token_id in enumerate(tokens_list):
				if index == 0:
					line += str(token_id)
				else:
					line += '; ' + str(token_id)
			fp.write(line + '\n')
		"""

		for path_id, tokens_list in paths_with_node_types_dictionary.items():
			line = str(path_id) + ', '
			for token in tokens_list:
				token = token.replace(' UP', ')^' )
				token = token.replace(' DOWN', ')_')
				line += '(' + token
			fp.write(line + '\n')


if __name__ == '__main__':
	args = sys.argv
	code2vec_input_data_folder, dataset_name = args[1], args[2]
	convert_astminer_files(code2vec_input_data_folder, dataset_name)
