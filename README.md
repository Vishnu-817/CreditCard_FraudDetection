# 💳 CreditCard Fraud Detection

An end-to-end Machine Learning and Streamlit web application for exploring financial transactions and detecting fraud in large-scale datasets.

---

## 📌 Project Overview

This repository features:
- **Interactive Streamlit Web Dashboard (`app.py`)**: Efficiently analyzes large transaction datasets in streaming chunks (100,000 rows/chunk), displaying key metrics, fraud rates by transaction type, breakdown charts, and filterable samples.
- **Machine Learning & EDA Pipeline (`main.ipynb`)**: Performs exploratory data analysis, outlier handling (Winsorization and IQR clipping), data preprocessing, and trains a supervised classification model (`DecisionTreeClassifier`) yielding **99.95% accuracy** and an **ROC-AUC of 0.9820**.

---

## 📊 Key Findings from Dataset

From 6,362,620 transactions (8,213 fraudulent, ~0.129% fraud rate):
- Fraud occurs exclusively in **`TRANSFER`** (0.769% fraud rate) and **`CASH_OUT`** (0.184% fraud rate) transaction types.
- Other transaction types (`PAYMENT`, `CASH_IN`, `DEBIT`) have 0 fraudulent transactions in this dataset.
- The severe class imbalance requires specialized classification metrics (Precision, Recall, F1-Score, and ROC-AUC) rather than standard regression or raw accuracy alone.

---

## 🛠️ Project Structure

```text
CreditCard_Fraud/
├── .gitignore               # Excludes large CSVs, models, and virtual environments
├── .streamlit/
│   └── config.toml          # Streamlit configuration (sets maxUploadSize to 600MB)
├── app.py                   # Streamlit dashboard application
├── main.ipynb               # Jupyter notebook with EDA, outlier treatment & ML model
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Vishnu-817/CreditCard_FraudDetection.git
cd CreditCard_FraudDetection
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```

The dashboard automatically loads `PS_20174392719_1491204439457_log.csv` if it exists in the root directory. If the dataset is not present, you can upload any compliant CSV (with `type`, `amount`, and `isFraud` columns) through the sidebar.

### 4. Run the Jupyter Notebook
Install Jupyter if it is not already available in your environment:
```bash
pip install jupyter
```

```bash
jupyter notebook main.ipynb
```

---

## 📈 Model Performance

| Metric | Score |
| :--- | :--- |
| **Accuracy** | 99.95% |
| **ROC-AUC** | 0.9820 |
| **Fraud Precision** | 92.17% |
| **Fraud Recall** | 63.79% |
| **Fraud F1-Score** | 0.7540 |

---

## 🌐 Deploying on Streamlit Community Cloud

1. Push this repository to GitHub (ensure the `.csv` file is ignored as configured in `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. Select your repository: `Vishnu-817/CreditCard_FraudDetection`.
4. Set the main file path to `app.py`.
5. Click **Deploy**.