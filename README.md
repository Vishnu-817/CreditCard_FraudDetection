# CreditCard Fraud Detection

A Streamlit dashboard for exploring transaction counts, fraud rates, and sampled
transactions from a CSV dataset.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app automatically uses `PS_20174392719_1491204439457_log.csv` when that
file is present beside `app.py`. Otherwise, upload a CSV from the sidebar.
The CSV must contain `type`, `amount`, and `isFraud` columns.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create an app from the repository.
3. Set the app's main file to `app.py`.
4. Deploy. Since the dataset is excluded from Git, upload it through the app
   or make it available through a separate data-hosting solution.

The dashboard reads data in chunks and displays a sample rather than loading
the entire dataset into its table. The current local dataset is about 494 MB;
confirm your hosting plan and available memory can handle uploading and
processing it before deployment.
