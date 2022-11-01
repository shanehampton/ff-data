from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RepeatedKFold
from xgboost import XGBRegressor
import pandas as pd


def decision_tree_regression(xtrain, xtest, ytrain, ytest, random_state, max_depth, min_samples_leaf, max_features, criterion):
    '''
    Base decision tree regression model
    '''
    model = DecisionTreeRegressor(random_state=random_state, max_depth=max_depth,
                                  min_samples_leaf=min_samples_leaf, max_features=max_features, criterion=criterion)
    model.fit(xtrain, ytrain)
    rsq = model.score(xtrain, ytrain)
    ypred = model.predict(xtest)
    mse = mean_squared_error(ypred, ytest)
    return {
        'max_depth': max_depth,
        'min_samples_leaf': min_samples_leaf,
        'max_features': max_features,
        'criterion': criterion,
        'rsq': rsq,
        'mse': mse,
        'model': model,
        'xtrain': xtrain,
        'xtest': xtest,
        'ytrain': ytrain,
        'ytest': ytest,
        'ypred': ypred
    }


def build_trees(x, y, random_state=None, max_depth_range=range(4, 9), min_samples_leaf_range=(5, 10, 15, 20, 25), max_features_range=(None, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), criterion_range=('squared_error', 'friedman_mse', 'absolute_error')):
    results = []
    xtrain, xtest, ytrain, ytest = train_test_split(
        x, y, test_size=0.1, random_state=random_state)
    for max_depth in max_depth_range:
        for min_samples_leaf in min_samples_leaf_range:
            for max_features in max_features_range:
                for criterion in criterion_range:
                    result = decision_tree_regression(xtrain, xtest, ytrain, ytest, random_state=random_state, max_depth=max_depth,
                                                      min_samples_leaf=min_samples_leaf, max_features=max_features, criterion=criterion)
                    results.append({**result, **{'test_size': 0.1}})
    return results


def find_optimal_tree(x, y, random_state=None, n=3):
    if random_state is None:
        results = []
        for _ in range(n):
            results.extend(build_trees(x, y))
    else:
        results = build_trees(x, y, random_state=random_state)
    results = sorted(results, key=lambda d: d['mse'])
    print(f'{len(results)} trees built')
    return results[0]


def run_xgboost(x, y, n_estimators: int, max_depth: int, learning_rate: float, min_child_weight: float, test_size: float = 0.2):
    '''
    Gradient-boosted decision tree regression ensemble via xgboost
    '''
    model = XGBRegressor(n_estimators=n_estimators, max_depth=max_depth,
                         learning_rate=learning_rate, min_child_weight=min_child_weight, colsample_bytree=1)
    xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=test_size)
    model.fit(xtrain, ytrain)
    rsq = model.score(xtrain, ytrain)
    ypred = model.predict(xtest)
    ypred_df = pd.DataFrame({'pred_points_pg': ypred}, index=xtest.index)
    mae = mean_absolute_error(ypred, ytest)
    comp = pd.concat([ytest, ypred_df], axis=1)
    comp['error'] = comp.pred_points_pg - comp.result_points_pg
    return {
        'model': model,
        'xtrain': xtrain,
        'xtest': xtest,
        'ytrain': ytrain,
        'ytest': ytest,
        'ypred': ypred,
        'rsq': rsq,
        'mae': mae,
        'comp': comp
    }


def xgboost_grid_search(x, y):
    '''
    Grid search through parameter space using xbgoost regression as a base model
    '''
    model = XGBRegressor()
    n_estimators = [50, 100, 150, 200]
    max_depth = [1, 2, 3, 4]
    learning_rate = [0.01, 0.1, 0.2, 0.3]
    min_child_weight = [1, 4, 7, 10]
    param_grid = dict(max_depth=max_depth, n_estimators=n_estimators,
                      learning_rate=learning_rate, min_child_weight=min_child_weight)
    cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=88)
    grid_search = GridSearchCV(
        model, param_grid, scoring='neg_mean_absolute_error', cv=cv, verbose=1)
    grid_result = grid_search.fit(x, y)
    return grid_result
