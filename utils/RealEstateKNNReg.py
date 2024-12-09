import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.neighbors import KNeighborsRegressor
from sklearn.inspection import permutation_importance
from sklearn.utils import resample
from sklearn.model_selection import train_test_split, RandomizedSearchCV, KFold, cross_val_score 
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler
from scipy.stats import randint
import shap

class RealEstateKNN:
    def __init__(self, dataset, target, n_neighbors, metric, weights, algorithm):
        """
        Initialize the KNN Regressor for real estate price prediction.
        """
        self.dataset = dataset
        self.target = target
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.weights = weights
        self.algorithm = algorithm 
        self.model = KNeighborsRegressor(n_neighbors=n_neighbors, metric=metric, weights=weights, algorithm=algorithm)
        self.metrics = {'Training set' : {}, 'Test set':{}}
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.y_pred_test = None
        self.feature_names = None

    def set_feature_target(self):
        """
        Remove the target column from the X set and set y as the target column.
        """
        X = self.dataset.drop([self.target],axis=1)
        y = self.dataset[self.target]
        self.dataset_split(X, y)

    def dataset_split(self, X, y, test_size=0.2):
        """
        Split the dataset into training and test set.
        """
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=9)
        self.property_type = self.X_test["Property type"]
        self.feature_names = X.columns if isinstance(X, pd.DataFrame) else None
        self.scale_features(self.X_train, self.X_test)        

    def scale_features(self, X_train, X_test):
        """
        Scale the features in the training and test set.
        """
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.X_train = X_train_scaled
        self.X_test = X_test_scaled

    def train_model(self):
        """
        Train the KNN Regressor.
        """
        self.model.fit(self.X_train, self.y_train)

    def predict(self, X):
        """
        Generate predictions for the given dataset.
        """
        return self.model.predict(X)

    def evaluate(self):
        """
        Evaluate the model on the training and test set and calculate metrics.
        """
        self.y_pred_test = self.predict(self.X_test)
        y_pred_train = self.predict(self.X_train)
        self.calculate_metrics(self.y_train, y_pred_train, 'Training set')
        self.calculate_metrics(self.y_test, self.y_pred_test, 'Test set')

    def calculate_smape(self, actual, pred):
        numerator = np.abs(actual - pred)
        denominator = (np.abs(actual) + np.abs(pred)) / 2
        return np.mean(numerator / denominator) * 100

    def calculate_metrics(self, actual, pred, set_type):
        self.metrics[set_type]['MAE'] = round( mean_absolute_error(actual, pred), 3)
        self.metrics[set_type]['RMSE'] = round( np.sqrt(mean_squared_error(actual, pred)), 3)
        self.metrics[set_type]['R2'] = round( r2_score(actual, pred), 3)
        self.metrics[set_type]['MAPE'] = round( mean_absolute_percentage_error(actual,pred) * 100, 3)
        self.metrics[set_type]['sMAPE'] = round( self.calculate_smape(actual, pred), 3)

    def generate_graphs(self):
        self.plot_ideal_fit()
        self.plot_error_rate()
        #self.plot_feature_importance()

    def plot_ideal_fit(self):
        """
        Visualize predictions (y_test vs. y_pred_test).
        """
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=self.y_test, y=self.y_pred_test, alpha=0.6)   
        plt.plot([min(self.y_test), max(self.y_test)], [min(self.y_test), max(self.y_test)], color='red', linewidth=2, linestyle='--', label='Ideal fit')
        plt.title('KNN Regression: Predicted vs Actual Prices')
        plt.xlabel('Actual Price')
        plt.ylabel('Predicted Price')
        plt.legend()
        plt.savefig('./figures/Ideal_fit.png')
        plt.clf()

    def print_metrics(self):
        print("\nEVALUATION METRICS\n####################")
        for dataset,stats in self.metrics.items():
            print("\n",dataset)
            for metric,value in stats.items():
                print(f"{metric} : {value}")

    def plot_error_rate(self):
        test_set = pd.DataFrame(self.property_type, columns=["Property type"])
        test_set["Property type"] = test_set["Property type"].map({1:"HOUSE", 0:"APARTMENT"})
        test_set['actual_price'] = self.y_test
        test_set['predicted_price'] = self.y_pred_test
        test_set['error'] = abs(test_set['actual_price'] - test_set['predicted_price'])
        # Categorize into bins
        test_set['price_bin'] = pd.cut(test_set['actual_price'],
                                       bins=[0, 250000, 500000, 1000000, 1500000, 3000000],
                                       labels=['0-250k', '250k-500k', '500k-1M', '1M-1.5M', '1.5M+'])

        # Plot mean error per bin
        plt.figure(figsize=(8, 6))
        sns.barplot(data=test_set, y='price_bin', x='error', hue='Property type', saturation =0.5)
        plt.xlabel('Price Range')
        plt.ylabel('Mean Absolute Error')
        plt.title('Error by Price Range')
        plt.savefig('./figures/Error_rates.png')
        plt.clf()

    def plot_feature_importance(self):
        results = permutation_importance(self.model, self.X_train, self.y_train, scoring='neg_mean_squared_error')
        importances = results.importances_mean  # Mean importance across shuffles
        std = results.importances_std  # Standard deviation
        feature_importance = pd.DataFrame({
            'Feature': self.feature_names,
            'Importance': importances,
            'StdDev': std
        })

        #Sort by importance
        feature_importance = feature_importance.sort_values(by='Importance', ascending=False)
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Importance', y='Feature', data=feature_importance, errorbar=None)
        plt.errorbar(feature_importance['Importance'], feature_importance['Feature'], xerr=feature_importance['StdDev'], fmt='o', color='red', label='Std Dev')
        plt.title('Feature Importance from Permutation Importance')
        plt.xlabel('Mean Importance')
        plt.ylabel('Features')
        plt.legend()
        plt.tight_layout()
        plt.savefig('./figures/Feature_importance.png')
        plt.clf()       