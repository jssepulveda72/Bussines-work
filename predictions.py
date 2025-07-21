import altair as alt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder



def data_preparation(df, variable):


    encoder = OneHotEncoder(sparse_output=False)

    encoded_categorical_features = encoder.fit_transform(df[['Item', 'Day of Week', 'Month', 'Year']])

    X = encoded_categorical_features
    y = df[variable]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

    return X_train, X_test, y_train, y_test, encoder

def model_training(df, variable):
    """
    Trains a Random Forest model on the provided DataFrame.
    """
    X_train, X_test, y_train, y_test, encoder = data_preparation(df, variable)

    model = RandomForestRegressor(max_depth = 3,
                               min_samples_leaf = 5,
                               min_samples_split = 6,
                              n_estimators = 150)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return model, mse, r2, encoder


def predict_new_values(new_values, model, encoder, variable):
    """
    Predicts new values using the trained model and encoder.
    """
    new_values_encoded = encoder.transform(new_values[['Item', 'Day of Week', 'Month', 'Year']])
    predictions = model.predict(new_values_encoded)

    new_values[variable] = predictions

    return new_values[['Item', 'Day of Week', 'Month', 'Year', variable]]

