from pathlib import Path

import pandas as pd

try:
    import streamlit as st  # type: ignore[import-not-found]
except ModuleNotFoundError as exc:
    raise SystemExit(
        "The 'streamlit' dependency is required to run this app. "
        "Install it with: pip install streamlit"
    ) from exc


DATA_PATH = Path(__file__).parent / "PS_20174392719_1491204439457_log.csv"
REQUIRED_COLUMNS = {"type", "amount", "isFraud"}
CHUNK_SIZE = 100_000
SAMPLE_PER_CHUNK = 500


def analyze_transactions(source: object) -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame]:
    """Read a CSV in chunks and return exact totals plus a small representative sample."""
    if hasattr(source, "seek"):
        source.seek(0)  # type: ignore[union-attr]

    header = pd.read_csv(source, nrows=0)
    missing = REQUIRED_COLUMNS.difference(header.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

    columns = ["type", "amount", "isFraud"]
    if "step" in header.columns:
        columns.insert(0, "step")

    totals: list[pd.DataFrame] = []
    samples: list[pd.DataFrame] = []
    row_count = 0
    fraud_count = 0
    amount_sum = 0.0
    amount_min: float | None = None
    amount_max: float | None = None

    if hasattr(source, "seek"):
        source.seek(0)  # type: ignore[union-attr]

    for chunk in pd.read_csv(source, usecols=columns, chunksize=CHUNK_SIZE):
        chunk["amount"] = pd.to_numeric(chunk["amount"], errors="coerce")
        chunk["isFraud"] = pd.to_numeric(chunk["isFraud"], errors="coerce")
        if chunk[["type", "amount", "isFraud"]].isna().any().any():
            raise ValueError("Required columns contain missing or non-numeric values.")
        if not chunk["isFraud"].isin([0, 1]).all():
            raise ValueError("'isFraud' must contain only 0 and 1.")

        chunk["isFraud"] = chunk["isFraud"].astype("int8")
        row_count += len(chunk)
        fraud_count += int(chunk["isFraud"].sum())
        amount_sum += float(chunk["amount"].sum())
        chunk_min = float(chunk["amount"].min())
        chunk_max = float(chunk["amount"].max())
        amount_min = chunk_min if amount_min is None else min(amount_min, chunk_min)
        amount_max = chunk_max if amount_max is None else max(amount_max, chunk_max)

        totals.append(
            chunk.groupby("type", observed=True).agg(
                transactions=("isFraud", "size"),
                fraud_transactions=("isFraud", "sum"),
                total_amount=("amount", "sum"),
            )
        )
        samples.append(
            chunk.sample(
                n=min(SAMPLE_PER_CHUNK, len(chunk)),
                random_state=42,
            )
        )

    if row_count == 0 or amount_min is None or amount_max is None:
        raise ValueError("The CSV contains no transactions.")

    by_type = pd.concat(totals).groupby(level=0, observed=True).sum()
    by_type["fraud_rate_percent"] = (
        by_type["fraud_transactions"] / by_type["transactions"] * 100
    )
    sample = pd.concat(samples, ignore_index=True)
    summary: dict[str, object] = {
        "transactions": row_count,
        "fraud_transactions": fraud_count,
        "fraud_rate_percent": fraud_count / row_count * 100,
        "average_amount": amount_sum / row_count,
        "minimum_amount": amount_min,
        "maximum_amount": amount_max,
    }
    return summary, by_type.sort_values("transactions", ascending=False), sample


st.set_page_config(page_title="Fraud Data Explorer", page_icon="🔎", layout="wide")
st.title("🔎 Fraud Transaction Explorer")
st.write(
    "Explore transaction totals, fraud rates, and a sample of the data. "
    "Metrics are calculated across the full CSV in chunks."
)

uploaded_file = st.sidebar.file_uploader("Upload the transaction CSV", type=["csv"])
if uploaded_file is not None:
    data_source: object = uploaded_file
    source_id = uploaded_file.name
    st.sidebar.success(f"Using uploaded file: {uploaded_file.name}")
elif DATA_PATH.is_file():
    data_source = DATA_PATH
    source_id = DATA_PATH.name
    st.sidebar.info(f"Using local file: {DATA_PATH.name}")
else:
    data_source = None
    source_id = None
    st.info("Upload the CSV to begin. On Streamlit Cloud, the local dataset is not included.")

# Reset dashboard if data source changes
if "current_source" in st.session_state and st.session_state["current_source"] != source_id:
    st.session_state.pop("fraud_dashboard", None)
st.session_state["current_source"] = source_id

if data_source is not None and st.button("Analyze transactions", type="primary"):
    with st.spinner("Reading and summarizing the CSV in chunks..."):
        try:
            summary, by_type, sample = analyze_transactions(data_source)
        except (OSError, ValueError, pd.errors.ParserError) as exc:
            st.error(f"Could not analyze this CSV: {exc}")
        else:
            st.session_state["fraud_dashboard"] = (summary, by_type, sample)

result = st.session_state.get("fraud_dashboard")
if result is not None:
    summary, by_type, sample = result
    st.subheader("Dataset overview")
    metric_columns = st.columns(4)
    metric_columns[0].metric("Transactions", f"{summary['transactions']:,}")
    metric_columns[1].metric("Fraud transactions", f"{summary['fraud_transactions']:,}")
    metric_columns[2].metric("Fraud rate", f"{summary['fraud_rate_percent']:.3f}%")
    metric_columns[3].metric("Average amount", f"${summary['average_amount']:,.2f}")
    st.caption(
        f"Transaction amount range: ${summary['minimum_amount']:,.2f} "
        f"to ${summary['maximum_amount']:,.2f}"
    )

    st.subheader("Transaction breakdown by type")
    st.dataframe(
        by_type.rename(
            columns={
                "transactions": "Total Transactions",
                "fraud_transactions": "Fraud Count",
                "total_amount": "Total Volume",
                "fraud_rate_percent": "Fraud Rate (%)",
            }
        ),
        use_container_width=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Transactions by type")
        st.bar_chart(by_type[["transactions"]])
    with col2:
        st.subheader("Fraud rate (%) by type")
        st.bar_chart(by_type[["fraud_rate_percent"]])

    st.subheader("Transaction sample")
    transaction_types = sorted(sample["type"].astype(str).unique())
    selected_types = st.multiselect(
        "Filter transaction types",
        options=transaction_types,
        default=transaction_types,
    )
    filtered_sample = sample[sample["type"].astype(str).isin(selected_types)]
    if filtered_sample.empty:
        st.info("No transactions match the selected filter.")
    else:
        st.dataframe(filtered_sample, use_container_width=True, hide_index=True)
    st.caption(
        f"Showing up to {len(sample):,} sampled rows, not the entire dataset."
    )
