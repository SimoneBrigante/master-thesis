import pandas as pd
from my_model import model

if __name__ == '__main__':

	data = pd.read_csv('../data/input.csv')
	test_size = 0.2

	best_grade_columns = [col for col in data.columns if 'best_grade' in col and 'time_to' not in col]

	X = data[best_grade_columns]
	y = data['exam']

	model(X, y, test_size)
