# Anomaly Detection Program using LOF Algorithm

This program is a web-based application that uses the Local Outlier Factor (LOF) algorithm to detect anomalies in a given dataset. The frontend of the application is built using React and the backend is built using Python and Flask.

# How to Run Frontend

To run the frontend part of the application, navigate to the UI folder in your terminal and run the following commands:
bash

```
npm install
npm start
```

This will start the frontend server on http://localhost:3000.

# Backend

To run the backend part of the application, navigate to the API folder in your terminal and run the following commands to install the required packages:
bash
```
pip install -r requirements.txt
```

After the packages are installed, run the Main.py file using the following command:
bash
```
python Main.py
```

This will start the backend server on http://localhost:5000.

# How to Use

1. Go to http://localhost:3000 from your browser.
2. Click on the Choose File button to select the data file you want to use to train the model. A sample data file is provided in the API folder.
3. Click on the Train button to train the model. After the model is trained successfully, you will get an alert.
4. Click on the Choose File button again toselect the data file you want to detect anomalies in.
5. Click on the Check button to detect anomalies in the selected dataset. A CSV file containing the anomalies will be downloaded automatically.
6. In the downloaded CSV file, -1 represents an anomaly and 1 represents a non-anomaly.

Note: The application encodes non-numeric values to numeric types. Any null values in the data are removed before processing. The program may crash for files that are not in the UTF-8 encoding. Please note that LOF is a density-based algorithm and may not work well with datasets that have widely varying density. In the upcoming prototype, LOF will be replaced by Principle Component Analysis (PCA), and an inbuilt null value handling function will be introduced.

# About API 3.0 (beta release)
In this API api we tried to overcome the limitations of API 2.2 which was that was not considering anomalies caused by multiple columns for example: if a user usually logins from a country suddenly he changes his country than that would also be considered as an anomaly. Some featers of the API 2.2 was depricated to make it stable it currently does'nt have feature to train and detect anomalies from the two different dataset. It take data from a dataset and straight away prints anomalus values from that.