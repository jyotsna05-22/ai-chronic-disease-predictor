# AI Chronic Disease Predictor

This project is an AI-based system that predicts possible chronic diseases using patient health data.

The system collects health parameters from the user and uses machine learning models to analyze the risk of diseases such as heart disease, kidney disease, liver disease, and others.

## Features

- User registration and login system
- Health assessment questionnaire
- Machine learning based disease prediction
- Dashboard showing prediction results
- Diet plan suggestions
- User profile management
- Statistics and health analysis

## Technologies Used

- Python
- Flask
- Machine Learning
- HTML
- CSS
- SQLite Database

## Project Structure
## Machine Learning Models

The system uses trained machine learning models to predict the probability of chronic diseases.

The datasets used include:

- Heart Disease Dataset
- Kidney Disease Dataset
- Liver Disease Dataset

The models are trained using Python and stored inside the **models/** directory.

The script `train_models.py` is used to train and update the machine learning models.

---

## System Workflow

1. User registers and logs into the system.
2. The user fills out a health assessment questionnaire.
3. The system processes the input data.
4. The trained machine learning model analyzes the data.
5. The system predicts the possible disease risk.
6. Results are displayed on the user dashboard.
7. The system provides diet plan suggestions based on the results.

---

## Database

The project uses **SQLite database** to store user data.

It stores:

- User registration information
- Login credentials
- Health assessment results
- Prediction history

---

## Screenshots

### Home Page
![Home Page](screenshots/home.png)

### Login Page
![Login Page](screenshots/login.png)

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Prediction Result
![Prediction Result](screenshots/result.png)

---

## Author

Jyotsna Pajuri

Final Year Student interested in AI, Data Analysis, and Machine Learning.

---

## Future Improvements

- Improve prediction accuracy with advanced models
- Add more chronic diseases
- Add graphical health reports
- Deploy the system as a cloud-based web application

