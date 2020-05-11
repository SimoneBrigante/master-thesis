import pandas as pd
from my_model import model


if __name__ == '__main__':
	X = pd.read_csv('../../my_code2vec/models_train_stdout/all_files_TF.test.c2v.vectors', sep=' ', header=None)
	y = pd.read_csv('../../my_code2vec/models_train_stdout/all_files_TF_for_model_y.csv', header=None)
	test_size = 0.2

	y = y.values.ravel()

	model(X, y, test_size)
