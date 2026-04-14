# 🔗 Blockchain Project (Flask + Python)

A simple blockchain-based web application built using **Python Flask**.  
This project demonstrates basic blockchain concepts along with a web interface for user interaction and data management.

---

## 🚀 Features

- User registration and data storage  
- Simple blockchain structure implementation  
- Block creation and linking using hash values  
- Flask web interface (HTML templates)  
- Image and file handling support  
- Session management  
- Database integration (PostgreSQL)  

---

## 🛠️ Tech Stack

- Python 🐍  
- Flask 🌐  
- HTML, CSS 🎨  
- PostgreSQL 🗄️  
- JavaScript (basic)  
- Blockchain (custom implementation)  

---

## 📁 Project Structure

blockchain/
│
├── change.py
├── requirements.txt
├── migrations/
├── static/
├── templates/
├── flask_session/
├── .gitignore
└── README.md

---

## ⚙️ Installation & Setup

### 1. Clone the repository

git clone https://github.com/your-username/blockchain.git
cd blockchain

---

### 2. Create virtual environment

python -m venv myenv

Activate environment:

myenv\Scripts\activate

---

### 3. Install dependencies

pip install -r requirements.txt

---

## 🐘 PostgreSQL Setup

### Install PostgreSQL
https://www.postgresql.org/download/windows/

### Create database

psql -U postgres

CREATE DATABASE login;

### Check database

\l

---

## ⚙️ Configure Database in Project

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/login'

db_config = {
    'dbname': 'login',
    'user': 'YOUR_USERNAME',
    'password': 'YOUR_PASSWORD',
    'host': 'localhost',
    'port': 5432
}

---

## 🚀 Run Project

python change.py

Open:
http://127.0.0.1:5000/

---

## 👨‍💻 Author

Martin Lurth Raj Gantyal

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
