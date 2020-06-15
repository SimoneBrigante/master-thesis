import json
import csv


def import_final_dictionary(path):
	with open(path, 'r') as file:
		dictionary = json.load(file)
		return dictionary


def make_csv(folder_path, dataset_name, dictionary):
	with open(folder_path + dataset_name + '_paths_stats.csv', 'w') as file:
		writer = csv.writer(file)
		writer.writerow(['path', 'real_passed_count', 'pred_passed_count', 'pred_passed_score',
						 'real_notpassed_count', 'pred_notpassed_count', 'pred_notpassed_score',
						 'diff_real', 'diff_pred'])
		for path, stats in dictionary.items():
			row = [path] + stats['passed'] + stats['notpassed'] + \
				  [abs(stats['passed'][0] - stats['notpassed'][0]), abs(stats['passed'][1] - stats['notpassed'][1])]
			writer.writerow(row)


def top_path_analyzer(final_dictionary):
	paths_stats = {}

	for _, content in final_dictionary.items():
		pred = content['predictions']
		real_exam_outcome = content['exam_outcome']
		predicted_exam_outcome = pred[0][1]

		for attention_item in content['attentions']:
			path_string = attention_item['path']
			attention_score = attention_item['score']

			if path_string not in paths_stats:
				paths_stats[path_string] = {
					'passed': [0, 0, 0],		# (real_count, pred_count, pred_score)
					'notpassed': [0, 0, 0]
				}
			# Increase counter of real outcome
			paths_stats[path_string][real_exam_outcome][0] += 1

			# Increase counter of predicted outcome
			paths_stats[path_string][predicted_exam_outcome][1] += 1

			# Increase scores of predictions
			paths_stats[path_string][pred[0][1]][2] += attention_score * pred[0][0]
			paths_stats[path_string][pred[1][1]][2] += attention_score * pred[1][0]

	return paths_stats


if __name__ == '__main__':
	folder_path = '../../code2vec_output_data/'

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
		path_to_final_dictionary = folder_path + dataset_name + '_final_dictionary.json'
		final_dictionary = import_final_dictionary(path_to_final_dictionary)

		paths_stats = top_path_analyzer(final_dictionary)

		make_csv(folder_path, dataset_name, paths_stats)
