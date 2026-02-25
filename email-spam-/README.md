
# Email Spam Detection Web Application

This is a simple **Flask-based web application** that allows users to:
- Register and login
- Send emails to other users
- Automatically classify emails as **Spam** or **Not Spam (Ham)**
- View emails in **Inbox** or **Spam** folders
- Logout securely using sessions

The focus of this project is **backend logic and machine learning**

---

## Features

- User registration and login
- Session-based authentication
- Compose and send emails between users
- Spam detection using Machine Learning
- Separate Inbox and Spam pages
- Logout functionality
- SQLite database for storage

---

## Technologies Used

- Python
- Flask (Web Framework)
- SQLite (Database)
- Scikit-learn (Machine Learning)
- Pandas (Data handling)
- HTML (Basic templates)

---

## Project Structure

mail_app/
│
├── app.py # Main Flask application
├── database.py # Database connection and table creation
├── model.py # Machine learning spam detection model
├── spam.csv # Dataset (1000 spam + 1000 ham)
│
└── templates/
├── login.html
├── inbox.html
├── compose.html
└── spam.html



---

## How the System Works

1. User registers with email and password
2. User logs in (session is created)
3. Inbox page opens after login
4. User can compose an email to another user
5. Before saving, the email text is checked by the ML model
6. If spam → saved in Spam folder  
   If not spam → saved in Inbox
7. Receiver logs in and sees the email
8. User can logout safely

---

## Machine Learning Model

- Algorithm: **Multinomial Naive Bayes**
- Feature Extraction: **TF-IDF Vectorizer**
- Dataset:
  - 1000 spam messages
  - 1000 ham (normal) messages
- Labels:
  - `spam` → 1
  - `ham` → 0

The model is trained **once at application startup**.

---


How to Test

Register two users

Login as User A

Compose an email to User B

Use spam text → goes to Spam

Use normal text → goes to Inbox

Logout

Login as User B

Check Inbox and Spam folders

Example Spam Text
Win cash now click here
Congratulations you won a free prize

Example Ham Text
Meeting scheduled tomorrow at 10 am
Please review the attached document

Limitations

Basic ML model (demo purpose)

No password hashing

No real email sending (internal system only)

Simple HTML (no advanced UI)

Future Improvements

Password hashing (bcrypt)

Email verification / OTP

Improved ML accuracy

Admin dashboard

Real email integration (SMTP)

Advanced UI (Gmail-like)

Project Use Case

This project is suitable for:

Final year project

Capstone project

Machine learning demonstration

Flask backend learning
=======
#  Email Spam Classifier (AI Capstone Project)

An AI-powered **Email Spam Classification Web Application** built using  
**Machine Learning (Naive Bayes)** and **Flask**.  
The system classifies emails as **Spam** or **Not Spam (Ham)** based on their content.

---

##  Project Overview

Email spam is a major problem in digital communication.  
This project uses **Natural Language Processing (NLP)** and **Machine Learning** to
automatically detect spam emails and provides a **web-based interface** for real-time testing.

---

##  Key Features

- ✔ Machine Learning based spam detection  
- ✔ TF-IDF text vectorization  
- ✔ Multinomial Naive Bayes classifier  
- ✔ Real-time email prediction  
- ✔ Web interface using Flask  
- ✔ Beginner-friendly & capstone-ready  

---

##  Technologies Used

- **Python**
- **Flask** (Web Framework)
- **Pandas**
- **NumPy**
- **Scikit-learn**
- **HTML & CSS**

---

##  Project Structure

Email-Spam-Classifier/
│
├── app.py # Flask web application
├── spam_classifier.py # ML model & prediction logic
├── spam.csv # Dataset
├── requirements.txt # Dependencies
├── README.md # Project documentation
│
├── templates/
│ └── index.html # Web UI
│
└── static/
└── style.css # Styling

