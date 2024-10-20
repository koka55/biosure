from sklearn.model_selection import train_test_split
from data.data_extraction import extract_data
from data.load_data import data_load
from data.preprocessing import processed_features
from data.model import create_model
from data.rigistry import save_model, load_model


def preprocess_and_train(folder_path_json):

    # extract data from json
    folder_path_csv = extract_data(folder_path_json)

    # load csv files to df
    data = data_load(folder_path_csv)

    # split the data
    # define X and y
    X = data.drop(columns='label')
    y = data['label']
    # split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # preprocess the data (train set and test set)
    X_train_processed = processed_features(X_train)
    X_test_processed = processed_features(X_test)


    # initializing the model
    model = create_model()

    # save_results(params=params, metrics=dict(mae=val_mae))
    # save_model(model=model)

    print("✅ preprocess_and_train() done")


def pred(folder_path_json):
     # extract data from json
    folder_path_csv = extract_data(folder_path_json)

    # load csv files to df
    X = data_load(folder_path_csv)

    # preprocess X
    X_processed = processed_features(X)

    # predicting
    model = load_model()
    y_pred = model.predict(X_processed)

    print(f"✅ pred() done")

    return y_pred



if __name__ == '__main__':
    try:
        preprocess_and_train()
        # preprocess()
        # train()
        pred()
    except:
        import sys
        import traceback

        import ipdb
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        ipdb.post_mortem(tb)
