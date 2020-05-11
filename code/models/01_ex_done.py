import pandas as pd
from my_model import model

if __name__ == '__main__':

	data = pd.read_csv('../data/input.csv')
	test_size = 0.2

	X = data.filter(regex='attempted')
	y = data['exam']

	model(X, y, test_size)
