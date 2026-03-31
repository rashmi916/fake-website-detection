# 🔐 Phishing Website Detection System

A machine learning-based web application that detects whether a given website URL is legitimate or phishing. The system uses a trained model to analyze URL features and provide real-time predictions through a user-friendly web interface.

---

## 🚀 Features

- 🔍 Detects phishing websites using Machine Learning
- 🌐 User-friendly web interface for URL input
- ⚡ Real-time prediction results
- 📊 Displays classification (Legitimate / Phishing)
- 🧠 Trained model using Scikit-learn
- 💾 Stores user queries/results using MySQL (optional feature)
- 📱 Responsive frontend design

---

## 🛠️ Technologies Used

### Frontend:
- HTML5  
- CSS3  
- JavaScript  

### Backend:
- Python  
- Flask  

### Machine Learning:
- Scikit-learn  

### Database:
- MySQL  

---

## 📂 Project Structure

---

## ⚙️ How It Works

1. User enters a website URL in the input field  
2. The system extracts important features from the URL  
3. The trained machine learning model analyzes the features  
4. The system predicts whether the URL is **Phishing** or **Legitimate**  
5. Result is displayed on the web interface  

---

## 💻 How to Run the Project

### 1. installation dependecies
pip install -r requirements.txt

### 2 Setup Database (MySQL)
Create a database in MySQL
Import db.sql file

### 3. Run the Application
python app.py
