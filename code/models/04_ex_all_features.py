import pandas as pd
from my_model import model

if __name__ == '__main__':

	data = pd.read_csv('../data/input.csv')
	test_size = 0.2

	X = data.drop('exam', axis=1)
	y = data['exam']

	# Delete constant features
	del X['REAL06_time_to_best_grade']
	del X['REAL12_time_to_best_grade']

	model(X, y, test_size)
