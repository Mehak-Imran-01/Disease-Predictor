# Disease Predictor 

An AI-powered web app that takes your symptoms as input and predicts potential diseases, helping users gain quick health insights..

---

## Features

- Input your symptoms and get disease predictions.  
- AI-powered prediction using a trained machine learning model.  
- Interactive and user-friendly interface.  
- Stores disease information and prediction history locally.

---

## Technologies Used

- **Backend:** Python, Flask  
- **Machine Learning:** Scikit-learn, Pandas, NumPy  
- **Frontend:** HTML, CSS   
- **Database:** MongoDB (for storing user queries or data)   

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Mehak-Imran-01/Disease-Predictor.git
cd Disease-Predictor
```


2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- (For windows)
```bash
venv\Scripts\activate
```

- (For MAC/Linux)
```bash
source venv/bin/activate
```

4. Install required packages:
```bash
pip install -r requirements.txt
```

5. Add your environment variables:
```bash
SECRET_KEY=your_secret_key
MONGO_URL=your_mongodb_url
```

6. Run the Flask app locally:
```bash
python app.py
```

7. Open your browser at:
```bash
http://127.0.0.1:5000
```

---
