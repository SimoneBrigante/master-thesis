import math

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV


def preprocessing(X, y, test_size):
	# Split Dataset
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=1)

	# Scale Data
	scaler_X = StandardScaler()
	X_train = scaler_X.fit_transform(X_train)
	X_test = scaler_X.transform(X_test)

	return X_train, X_test, y_train, y_test


def model(X, y, test_size):
	print('Samples: {} - Passed: {} ({:.2f}) - Test Set: {}'.format(len(y), sum(y), sum(y) / len(y), math.ceil(len(y) * test_size)))
	print('# Features: {}'.format(len(X.columns)))

	X_train, X_test, y_train, y_test = preprocessing(X, y, test_size)

	gradient_boosting_clf = GradientBoostingClassifier()

	gradient_boosting_clf.fit(X_train, y_train)

	accuracies = cross_val_score(estimator=gradient_boosting_clf, X=X_train, y=y_train, cv=10, n_jobs=-1)
	print("\nCross Validation\n\tMean: {} - Std: {}".format(accuracies.mean(), accuracies.std()))

	# Confusion Matrix
	y_pred = gradient_boosting_clf.predict(X_test)
	clf_confusion_matrix = confusion_matrix(y_test, y_pred, labels=[1, 0])
	print("\nConfusion matrix:\n{}\n".format(clf_confusion_matrix))
