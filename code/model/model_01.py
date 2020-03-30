import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time

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


def k_best_features(X, y, k='all'):
	functions = {'mutual_info_classif': mutual_info_classif, 'f_classif': f_classif}
	scores = []
	names = X.columns.values
	for name, function in functions.items():
		selector = SelectKBest(function, k=k)
		X_fs = selector.fit_transform(X, y)
		scores.append(selector.scores_[selector.get_support()])

	mutual_info_names_scores = list(zip(names, scores[0]))
	f_class_names_scores = list(zip(names, scores[1]))
	mutual_info_df = pd.DataFrame(data=mutual_info_names_scores, columns=['Feat Name', 'mutual_info_classif'])
	f_class_df = pd.DataFrame(data=f_class_names_scores, columns=['Feat Name', 'f_classif'])
	mutual_info_df_sorted = mutual_info_df.sort_values(['mutual_info_classif', 'Feat Name'], ascending=[False, True])
	f_class_df_sorted = f_class_df.sort_values(['f_classif', 'Feat Name'], ascending=[False, True])
	print(mutual_info_df_sorted)
	print(f_class_df_sorted)
	f_class_df_sorted.to_excel('../data/features_f_class.xlsx')
	plot_graph_features(X, y, list(f_class_df_sorted['Feat Name'][:9]))


def plot_graph_features(X, y, features):
	# Conta frequenza di ogni coppia <voto_esercizio, pass/no_pass>
	fig, axs = plt.subplots(3, 3)
	plt.subplots_adjust(wspace=0.5, hspace=0.5)
	for num_feat, feature in enumerate(features):
		cases_per_coordinate = {}
		# print("Feature: {} - len(X): {} - len(y): {}".format(feature, len(X[feature]), len(y)))
		for index in range(len(X[feature])):
			# key = {'x': normalized_X[column][index], 'y': y[index]}
			key = tuple([X[feature][index], y[index]])
			if key not in cases_per_coordinate:
				cases_per_coordinate[key] = {'x': X[feature][index], 'y': y[index], 'z': 0}
			cases_per_coordinate[key]['z'] += 1

		x_graph = []
		y_graph = []
		z_graph = []

		for value in cases_per_coordinate.values():
			x_graph.append(value['x'])
			y_graph.append(value['y'])
			z_graph.append(value['z'])

		axs[num_feat // 3, num_feat % 3].scatter(x_graph, y_graph, s=z_graph, alpha=0.5)
		# plt.scatter(x_graph, y_graph, s=z_graph*40000)
		# axs[num_feat // 3, num_feat % 3].set_title(feature)
		# axs[num_feat // 3, num_feat % 3].ylabel('Exam')
		for i, z in enumerate(z_graph):
			if z > 5:
				axs[num_feat // 3, num_feat % 3].annotate(z, (x_graph[i], y_graph[i]))

	for index, ax in enumerate(axs.flat):
		ax.set(xlabel=features[index], ylabel='Exam')
	plt.show()


def grid_search(X, y):
	X_train, X_test, y_train, y_test = preprocessing(X, y)

	parameters = {
		"loss": ["deviance", "exponential"],
		"learning_rate": [0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2],
		"n_estimators": [10],
		"subsample": [0.5, 0.618, 0.8, 0.85, 0.9, 0.95, 1.0],
		"criterion": ["friedman_mse",  "mae"],
		"min_samples_split": np.linspace(0.1, 0.5, 12),
		"min_samples_leaf": np.linspace(0.1, 0.5, 12),
		"max_depth": [3, 5, 8],
		"max_features": ["log2", "sqrt", None],
	}
	best_params = {
		'criterion': 'friedman_mse',
		'learning_rate': 0.2,
		'loss': 'exponential',
		'max_depth': 8,
		'max_features': None,
		'min_samples_leaf': 0.1,
		'min_samples_split': 0.13636363636363638,
		'n_estimators': 10,
		'subsample': 0.8
	}		# 0.8306451612903226
	parameters = {
		"loss": ["deviance", "exponential"],
		"learning_rate": np.linspace(0.1, 1, 10),
		"n_estimators": [5, 10, 15,  20],
		"subsample": [0.5, 0.8, 0.9, 1.0],
		"criterion": ["friedman_mse",  "mae"],
		"min_samples_split": np.linspace(0.1, 0.5, 5),
		"min_samples_leaf": np.linspace(0.1, 0.5, 5),
		"max_depth": [5, 8, 10, 15],
		"max_features": ["log2", "sqrt", None],
	}
	best_params = {
		'criterion': 'friedman_mse',
		'learning_rate': 0.2,
		'loss': 'deviance',
		'max_depth': 5,
		'max_features': None,
		'min_samples_leaf': 0.1,
		'min_samples_split': 0.1,
		'n_estimators': 15,
		'subsample': 0.5
	}		# 0.8440860215053764

	clf = GridSearchCV(GradientBoostingClassifier(), parameters, cv=10, n_jobs=-1, verbose=1)

	clf.fit(X_train, y_train)
	print(clf.score(X_train, y_train))
	print(clf.best_params_)


def important_features_in_k_attempts(X, y, k=10):
	features_after_k = {}

	time_start = time.time()

	for i in range(k):

		clf = model(X, y, 0)

		# Extract most important features
		feature_importances = clf.feature_importances_
		feature_names = X.columns.values
		features = list(zip(feature_names, feature_importances))						# merge features name and importance_score
		features = [(name, value) for name, value in features if value > 0]				# Remove features with score = 0
		sorted_features = sorted(features, key=lambda tup: tup[1], reverse=True)		# Sort features by importance_score

		for index, tuple in enumerate(sorted_features):
			if tuple[0] not in features_after_k:
				features_after_k[tuple[0]] = 0
			features_after_k[tuple[0]] += tuple[1]
			# print("{:2d}) {:50s} - {:.5f}".format(index + 1, tuple[0], tuple[1]))

	sorted_features_after_k = sorted(features_after_k.items(), key=lambda item: item[1], reverse=True)
	print("Best Features:")
	for index, tuple in enumerate(sorted_features_after_k):
		if index >= 50:
			break
		print("{:2d}) {:50s} - {:.5f}".format(index + 1, tuple[0], tuple[1]))

	print("Time: {:.5f}".format(time.time() - time_start))


def model(X, y, verbose=1):
	X_train, X_test, y_train, y_test = preprocessing(X, y)

	# Create model with best parameters according GridSearch
	best_params = {
		'loss': 'deviance',
		'learning_rate': 0.2,
		'n_estimators': 15,
		'subsample': 0.5,
		'criterion': 'friedman_mse',
		'min_samples_split': 0.1,
		'min_samples_leaf': 0.1,
		'max_depth': 5,
		'max_features': None
	}		# 0.8440860215053764
	gradient_boosting_clf = GradientBoostingClassifier(
		loss='deviance', learning_rate=0.2, n_estimators=15, subsample=0.5, criterion='friedman_mse',
		min_samples_split=0.1, min_samples_leaf=0.1, max_depth=5, max_features=None, verbose=0)

	# Fit the model
	gradient_boosting_clf.fit(X_train, y_train)

	if verbose > 0:
		# Cross Validation to compute score of estimator
		accuracies = cross_val_score(estimator=gradient_boosting_clf, X=X_train, y=y_train, cv=10, n_jobs=-1)
		print("\nCross Validation\n\tMean: {} - Std: {}".format(accuracies.mean(), accuracies.std()))

		# Confusion Matrix
		y_pred = gradient_boosting_clf.predict(X_test)
		clf_confusion_matrix = confusion_matrix(y_test, y_pred)
		print("\nConfusion matrix:\n{}\n".format(clf_confusion_matrix))

	# Gradient Boosting with Feature Selection
	# TODO: Consider to use top 50 features_after_100000
	"""
	# Feature Selection - Select K best features according to f_classif
	selector = SelectKBest(f_classif, k=30)
	X_fs = selector.fit_transform(X, y)
	
	# Create a Dataframe of just Best Features
	names = X.columns.values[selector.get_support()]
	scores = selector.scores_[selector.get_support()]
	names_scores = list(zip(names, scores))
	ns_df = pd.DataFrame(data=names_scores, columns=['Feat_names', 'f_classif'])
	
	#Sort the dataframe for better visualization
	ns_df_sorted = ns_df.sort_values(['f_classif', 'Feat_names'], ascending=[False, True])
	
	# Split data
	X_fs_train, X_fs_test, y_fs_train, y_fs_test = preprocessing(X_fs, y)
	
	# Create and Fit Model
	gradient_boosting_fs_clf = GradientBoostingClassifier().fit(X_fs_train, y_fs_train)
	
	# Model Results
	y_gb_fs_pred = gradient_boosting_fs_clf.predict(X_fs_test)
	gb_fs_score = gradient_boosting_fs_clf.score(X_fs_test, y_fs_test)
	gb_fs_confusion_matrix = confusion_matrix(y_fs_test, y_gb_fs_pred)
	print("Gradient Boosting fs score: {}".format(gb_fs_score))
	print("Confusion matrix fs:\n{}".format(gb_fs_confusion_matrix))
	"""

	return gradient_boosting_clf


if __name__ == '__main__':

	data = pd.read_csv('../data/input.csv')
	X = data.drop('exam', axis=1)
	y = data['exam']

	print("# Samples: {} - # Exam Passed: {} ({:.2f})\n".format(len(y), sum(y), sum(y)/len(y)))

	# Delete constant features
	del X['REAL06_time_to_best_grade']
	del X['REAL12_time_to_best_grade']

	# Compute best features with SelectKBest
	# k_best_features(X, y)

	# GridSearchCV for best hyper-parameters - NB: really long time
	# grid_search(X, y)

	# Compute best features by fitting the model k times
	important_features_in_k_attempts(X, y, 1)

	model(X, y)






