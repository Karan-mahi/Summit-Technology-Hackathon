import pandas as pd
import ipaddress
import numpy as np
from sklearn.preprocessing import LabelEncoder
from flask import Flask, request, jsonify, send_file
from sklearn.neighbors import LocalOutlierFactor
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)
encoder = LabelEncoder()
lof_IP_Address = LocalOutlierFactor(n_neighbors=9, contamination=0.05)
lof_Country = LocalOutlierFactor(n_neighbors=15, contamination=0.05)
lof_Region = LocalOutlierFactor(n_neighbors=9, contamination=0.05)
lof_City = LocalOutlierFactor(n_neighbors=9, contamination=0.05)
lof_Browser_Name_and_Version = LocalOutlierFactor(n_neighbors=5, contamination=0.05)
lof_Device_Type = LocalOutlierFactor(n_neighbors=9, contamination=0.05)


def preprocess_data(df):
    df['IP Address'] = df['IP Address'].apply(str).apply(ipaddress.IPv4Address).apply(np.uint64)
    categorical_features = ['Country', 'Region',
                            'City', 'Browser Name and Version', 'Device Type']
    for feature in categorical_features:
        df[feature] = encoder.fit_transform(df[feature])
    return df


@app.route('/train_model', methods=['POST'])
def train_model():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    # Load the CSV file for training
    train_df = pd.read_csv(file)
    train_df = preprocess_data(train_df)

    lof_IP_Address.fit(train_df[["IP Address"]])
    lof_Country.fit(train_df[["Country"]])
    lof_Region.fit(train_df[["Region"]])
    lof_City.fit(train_df[["City"]])
    lof_Browser_Name_and_Version.fit(train_df[["Browser Name and Version"]])
    lof_Device_Type.fit(train_df[["Device Type"]])

    return jsonify({'message': 'Model trained successfully'})


@app.route('/detect_anomalies', methods=['POST'])
def detect_anomalies():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    # Load the CSV file
    df = pd.read_csv(file)

    # Preprocess the data
    df_preprocessed = df.copy()
    df_preprocessed = preprocess_data(df_preprocessed)

    df["Anomaly in IP Address"] = lof_Device_Type.fit_predict(df_preprocessed[["IP Address"]])
    df["Anomaly in Country"] = lof_Country.fit_predict(df_preprocessed[["Country"]])
    df["Anomaly in Region"] = lof_Region.fit_predict(df_preprocessed[["Region"]])
    df["Anomaly in City"] = lof_City.fit_predict(df_preprocessed[["City"]])
    df["Anomaly in Browser Name and Version"] = lof_Browser_Name_and_Version.fit_predict(
        df_preprocessed[["Browser Name and Version"]])
    df["Anomaly in Device Type"] = lof_Device_Type.fit_predict(df_preprocessed[["Device Type"]])

    new_df = df[((df['Login Successful']) & ((df['Anomaly in IP Address'] == -1) | (df['Anomaly in Country'] == -1) |
                                             (df['Anomaly in Region'] == -1) | (df['Anomaly in City'] == -1) |
                                             (df['Anomaly in Browser Name and Version'] == -1) | (
                                                     df['Anomaly in Device Type'] == -1)))]
    # Save the DataFrame as a CSV file
    new_df.to_csv('my_data.csv', index=False, mode='w')

    return send_file('my_data.csv', mimetype='text/csv', as_attachment=True)


if __name__ == '__main__':
    app.run()
