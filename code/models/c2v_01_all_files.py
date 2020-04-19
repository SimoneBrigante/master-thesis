import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif, chi2
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV


def preprocessing(X, y):
	# Split Dataset
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=1)

	# Scale Data
	scaler_X = StandardScaler()
	X_train = scaler_X.fit_transform(X_train)
	X_test = scaler_X.transform(X_test)

	return X_train, X_test, y_train, y_test


def model(X, y):
	X_train, X_test, y_train, y_test = preprocessing(X, y)

	gradient_boosting_clf = GradientBoostingClassifier()

	gradient_boosting_clf.fit(X_train, y_train)

	accuracies = cross_val_score(estimator=gradient_boosting_clf, X=X_train, y=y_train, cv=10, n_jobs=-1)
	print("\nCross Validation\n\tMean: {} - Std: {}".format(accuracies.mean(), accuracies.std()))

	# Confusion Matrix
	y_pred = gradient_boosting_clf.predict(X_test)
	clf_confusion_matrix = confusion_matrix(y_test, y_pred)
	print("\nConfusion matrix:\n{}\n".format(clf_confusion_matrix))


if __name__ == '__main__':
	X = pd.read_csv('../../my_code2vec/models_train_stdout/all_files.test.c2v.vectors', sep=' ', header=None)
	y = pd.read_csv('../../my_code2vec/models_train_stdout/all_files_TF_for_model_y.csv', header=None)

	y = y.values.ravel()

	print('Len X: {}'.format(len(X)))
	print('Len y: {}'.format(len(y)))

	print(y[:10])

	model(X, y)
