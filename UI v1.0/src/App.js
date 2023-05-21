import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  const [file, setFile] = useState(null);
  const [action, setAction] = useState('');
  const [result, setResult] = useState('');
  const [fileName, setFileName] = useState('');
  const [showConfirmation, setShowConfirmation] = useState(false);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile); // Set the selected file to the state
    setFileName(selectedFile.name); // Set the file name
  };

  const handleAction = (selectedAction) => {
    setShowConfirmation(true);
    setAction(selectedAction); // Set the selected action
  };

  const handleConfirmation = () => {
    setShowConfirmation(false);
    performAction();
  };

  const performAction = () => {
    const formData = new FormData();
    formData.append('file', file); // Append the file to the FormData object

    let apiUrl = '';
    if (action === 'check') {
      apiUrl = 'http://localhost:5000/detect_anomalies'; // Set the API endpoint for checking transaction anomaly
    } else if (action === 'train') {
      apiUrl = 'http://localhost:5000/train_model'; // Set the API endpoint for training the model
    }

    axios({
      url: apiUrl,
      method: 'POST',
      data: formData
    })
      .then((response) => {
        if (apiUrl === 'http://localhost:5000/detect_anomalies') {
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', 'my_data.csv'); // Set the file name
          document.body.appendChild(link);
          link.click();
        } else if (apiUrl === 'http://localhost:5000/train_model') {
          alert(response.data.message);
        }
      })
      .catch((error) => {
        console.error(error);
      });

    // axios
    //   .post(apiUrl, formData)
    //   .then((response) => {
    //     // setResult(response.data); // Update the result state with the API response
    //     // setFile(null); // Reset the file
    //     // setFileName(''); // Reset the file name
    //   })
    //   .catch((error) => {
    //     console.error(error);
    //   });
  };

  return (
    <div className="container">
      <h2>Welcome to Transaction Anomaly Checker</h2>
      <p>
        This website allows you to check transaction anomalies by uploading a file containing transaction data.
        Choose an action below to perform the desired operation.
      </p>
      <div className="upload-container">
        <label htmlFor="file-upload" className="upload-button-label">
          
          <input
            id="file-upload"
            type="file"
            onChange={handleFileChange}
            accept=".txt,.pdf,.xlsx"
          />
        </label>
        {fileName && <p className="file-name">{fileName}</p>}
      </div>
      <div className="button-container">
        <button
          className={`action-button ${action === 'check' ? 'active' : ''}`}
          onClick={() => handleAction('check')}
        >
          Check
        </button>
        <button
          className={`action-button ${action === 'train' ? 'active' : ''}`}
          onClick={() => handleAction('train')}
        >
          Train
        </button>
      </div>
      {showConfirmation && (
        <div className="confirmation-modal">
          <p>Are you sure you want to perform this action?</p>
          <div className="button-container">
            <button className="confirm-button" onClick={handleConfirmation}>
              Yes
            </button>
            <button
              className="cancel-button"
              onClick={() => setShowConfirmation(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
      <div>
        {/* <h3>Result:</h3> */}
        <p>{result}</p>
      </div>
    </div>
  );
};

export default App;
