'''
Preprocessing Data (Scaling: MinMax for numerical, and OneHotEncoder for categorical)
'''

import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.compose import make_column_transformer
from sklearn.ensemble import RandomForestClassifier

import xgboost as xgb

def create_model():
    rf_pipeline = Pipeline(steps=[
        ('classifier', RandomForestClassifier())
    ])

    rf_pipeline

    svc_pipeline = Pipeline(steps=[
        ('classifier', SVC())
    ])

    svc_pipeline

    xgb_pipeline = Pipeline(steps=[
        ('classifier', xgb())
    ])

    xgb_pipeline

    #return _pipeline
