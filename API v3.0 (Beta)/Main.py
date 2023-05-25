import pandas as pd
import ipaddress
import numpy as np
from sklearn.preprocessing import LabelEncoder
from flask import Flask, request, jsonify, send_file
from sklearn.ensemble import IsolationForest
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)
encoder = LabelEncoder()


def give_hours(time_str):
    hours, minutes = map(float, time_str.split(":"))
    return hours % 24


def preprocess_data(df):
    df['IP Address'] = df['IP Address'].apply(str).apply(ipaddress.IPv4Address).apply(np.uint64)
    categorical_features = ['Country', 'Region',
                            'City', 'Browser Name and Version', 'Device Type']
    for feature in categorical_features:
        df[feature+"_code"] = encoder.fit_transform(df[feature])
    df['Hours'] = df['Login Timestamp'].apply(give_hours)
    return df


def find_anomalies_in_uid_time(anomalies, df):
    # Create a dictionary where keys are the unique values of
    # column A and values are the corresponding values of column B
    uid_hour_dict = {}
    for _, row in df.iterrows():
        uid_hour_dict.setdefault(row['User ID'], []).append(row['Hours'])

    # Create a new DataFrame where each row represents a unique value of column A
    # and the corresponding values of column B are represented as a list
    new_df = pd.DataFrame(list(uid_hour_dict.items()), columns=['User ID', 'Hours'])
    models_uid_time = {}
    for _, row in new_df.iterrows():
        model = IsolationForest(n_estimators=100, contamination=0.05)
        x = np.array(row['Hours']).reshape(-1, 1)
        model.fit(x)
        models_uid_time[row['User ID']] = model

    # Predict anomalies in the original DataFrame
    for _, row in df.iterrows():
        if row['User ID'] in models_uid_time:
            model = models_uid_time[row['User ID']]
            y_pred = model.predict(np.array(row['Hours']).reshape(-1, 1))[0]
            if y_pred == -1:
                anomalies.append({'Login Timestamp': row['Login Timestamp'],
                                  'User ID': row['User ID'],
                                  'IP Address': row['IP Address'],
                                  'Country': row['Country'],
                                  'Region': row['Region'],
                                  'City': row['City'],
                                  'Browser Name and Version': row['Browser Name and Version'],
                                  'Device Type': row['Device Type'],
                                  'Login Successful': row['Login Successful'],
                                  'reason': 'User Login on unusual time'})

def find_anomalies_in_cluster(anomalies, df, a, b, reason):
    # Create a dictionary where keys are the unique values of
    # column A and values are the corresponding values of column B
    dict = {}
    for _, row in df.iterrows():
        dict.setdefault(row[a], []).append(row[b])

    # Create a new DataFrame where each row represents a unique value of column A
    # and the corresponding values of column B are represented as a list
    new_df = pd.DataFrame(list(dict.items()), columns=[a, b])
    models = {}
    for _, row in new_df.iterrows():
        model = IsolationForest(n_estimators=100, contamination=0.05)
        x = np.array(row[b]).reshape(-1, 1)
        model.fit(x)
        models[row[a]] = model

    # Predict anomalies in the original DataFrame
    for _, row in df.iterrows():
        if row[a] in models:
            model = models[row[a]]
            y_pred = model.predict(np.array(row[b]).reshape(-1, 1))[0]
            if y_pred == -1:
                anomalies.append({'Login Timestamp': row['Login Timestamp'],
                                  'User ID': row['User ID'],
                                  'IP Address': row['IP Address'],
                                  'Country': row['Country'],
                                  'Region': row['Region'],
                                  'City': row['City'],
                                  'Browser Name and Version': row['Browser Name and Version'],
                                  'Device Type': row['Device Type'],
                                  'Login Successful': row['Login Successful'],
                                  'Hours': row['Hours'],
                                  'reason': reason})

'''
    This route is currently depricated in this version for development purposes
'''
@app.route('/train_model', methods=['POST'])
def train_model():
    return jsonify({'message': 'Model trained successfully'})


@app.route('/detect_anomalies', methods=['POST'])
def detect_anomalies():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    # Load the CSV file for training
    df = pd.read_csv(file)
    df = df.iloc[:50]  ##remove this
    df = preprocess_data(df)
    df.loc[0, 'Hours'] = 17.0 ##remove this
    # for user - time relationship
    anomalies = []
    # find_anomalies_in_uid_time(anomalies, df)
    find_anomalies_in_cluster(anomalies, df, 'User ID', 'Hours', "User Login outside usual time")
    find_anomalies_in_cluster(anomalies, df, 'Country', 'Hours', "Suspicious login time for this country")
    find_anomalies_in_cluster(anomalies, df, 'Country', 'Hours', "Suspicious login time for this country")
    
    '''Isolation forest won't work well for these anomalies switching to LoF ASAP'''
    
    find_anomalies_in_cluster(anomalies, df, 'IP Address', 'Country_code', "IP Address doesn't match country")
    find_anomalies_in_cluster(anomalies, df, 'IP Address', 'Region_code', "Your Location Seems to change")
    find_anomalies_in_cluster(anomalies, df, 'IP Address', 'City_code', "Your Location Seems to change")
    find_anomalies_in_cluster(anomalies, df, 'IP Address', 'Login Successful',
                              "Too many Unsuccessful attempts from network")
    find_anomalies_in_cluster(anomalies, df, 'Country', 'Browser Name and Version_code',
                              "Outdated/Suspicious browser")
    find_anomalies_in_cluster(anomalies, df, 'Country', 'Device Type_code',
                              "This device is rarely using in this country")

    print(anomalies)

    return jsonify({'message': 'Detected'})


if __name__ == '__main__':
    app.run()
