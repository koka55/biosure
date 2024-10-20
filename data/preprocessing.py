'''
Preprocessing Data (Scaling: MinMax for numerical, and OneHotEncoder for categorical)
'''

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import make_column_transformer

def processed_features(X):
    def create_preproc():
        num_transformer = MinMaxScaler()
        cat_transformer = OneHotEncoder()


        preproc = make_column_transformer(
            (num_transformer, ['dwell_avg',	'flight_avg', 'traj_avg', 'keyboard_avg', 'mouse_avg', 'freq_mouse', 'freq_key']),
            (cat_transformer, ['day_type'])
        )
        return preproc

    if flag == False:

        preprocessor = create_preproc()
        X_processed = preprocessor.fit_transform(X)
        flag = True

    else:
        X_processed = preprocessor.transform(X)

    return X_processed
