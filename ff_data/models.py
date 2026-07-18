from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RepeatedKFold
from xgboost import XGBRegressor
import pandas as pd
import json


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


def run_xgboost(
    x: pd.DataFrame,
    y: pd.DataFrame,
    n_estimators: int,
    max_depth: int,
    learning_rate: float,
    min_child_weight: float,
    colsample_bytree: float,
    subsample: float,
    test_size: float = 0.2
):
    '''
    Gradient-boosted decision tree regression ensemble via xgboost
    '''
    model = XGBRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        min_child_weight=min_child_weight,
        colsample_bytree=colsample_bytree,
        subsample=subsample
    )
    xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=test_size)
    model.fit(xtrain, ytrain)
    rsq = model.score(xtrain, ytrain)
    ypred = model.predict(xtest)
    ypred_df = pd.DataFrame({'result_pred': ypred}, index=ytest.index)
    mae = mean_absolute_error(ytest, ypred)
    rmse = mean_squared_error(ytest, ypred, squared=False)
    comp = pd.concat([ytest, ypred_df], axis=1)
    comp['error'] = comp.result_pred - comp.result
    comp['error_abs'] = comp.error.abs()
    comp = comp.astype(float).round(1)
    return {
        'model': model,
        'xtrain': xtrain,
        'xtest': xtest,
        'ytrain': ytrain,
        'ytest': ytest,
        'ypred': ypred,
        'rsq': rsq,
        'mae': mae,
        'rmse': rmse,
        'comp': comp
    }


def xgboost_grid_search(
    x: pd.DataFrame,
    y: pd.DataFrame,
    n_estimators: list = None,
    max_depth: list = None,
    learning_rate: list = None,
    min_child_weight: list = None,
    gamma: list = None,
    alpha: list = None,
    reg_lambda: list = None,
    colsample_bytree: list = None,
    colsample_bylevel: list = None,
    colsample_bynode: list = None,
    subsample: list = None,
    n_splits: int = 10,
    n_repeats: int = 3,
    scoring: str = 'neg_root_mean_squared_error'
):
    '''
    Grid search through parameter space using xbgoost regression as a base model
    '''
    model = XGBRegressor()
    param_grid = dict()
    if n_estimators:
        param_grid['n_estimators'] = n_estimators
    if max_depth:
        param_grid['max_depth'] = max_depth
    if learning_rate:
        param_grid['learning_rate'] = learning_rate
    if min_child_weight:
        param_grid['min_child_weight'] = min_child_weight
    if gamma:
        param_grid['gamma'] = gamma
    if alpha:
        param_grid['alpha'] = alpha
    if reg_lambda:
        param_grid['reg_lambda'] = reg_lambda
    if colsample_bytree:
        param_grid['colsample_bytree'] = colsample_bytree
    if colsample_bylevel:
        param_grid['colsample_bylevel'] = colsample_bylevel
    if colsample_bynode:
        param_grid['colsample_bynode'] = colsample_bynode
    if subsample:
        param_grid['subsample'] = subsample
    print(f'param_grid:\n{json.dumps(param_grid, indent=4)}\n')
    cv = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats)
    grid_search = GridSearchCV(
        model,
        param_grid,
        scoring=scoring,
        cv=cv,
        verbose=1
    )
    grid_result = grid_search.fit(x, y)
    return grid_result
