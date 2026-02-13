import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Reduce top padding so title is at the very top
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load Excel file
df = pd.read_excel("KafkaReport.xlsx", engine="openpyxl")

df["App"] = df["App"].astype(str).str.strip()
df["Sl.No"] = df.groupby("App").cumcount() + 1
df["StatusCategory"] = df["Status"].str.lower().apply(
    lambda x: "Completed" if "prod" in x else "Pending"
)

st.title("Kafka Report Dashboard")

# Dropdown filter (default = Pending)
filter_option = st.selectbox(
    "Filter by Status",
    options=["All", "Completed", "Pending"],
    index=2
)

# Add space after dropdown
st.markdown("<br><br>", unsafe_allow_html=True)

# Apply filter
if filter_option == "Completed":
    filtered_df = df[df["StatusCategory"] == "Completed"]
elif filter_option == "Pending":
    filtered_df = df[df["StatusCategory"] == "Pending"]
else:
    filtered_df = df.copy()

# Loop through apps in filtered data
for app in filtered_df["App"].unique():
    st.header(f"App: {app}")
    app_df = filtered_df[filtered_df["App"] == app].reset_index()

    # Single editable grid: only Status column editable
    edited_app_df = st.data_editor(
        app_df.head(30)[["Sl.No", "Type", "Emp", "Kafka", "Status"]],
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Sl.No": st.column_config.TextColumn(
                disabled=True,
                width="small"   # compact numbering column
            ),
            "Type": st.column_config.TextColumn(disabled=True, width="medium"),
            "Emp": st.column_config.TextColumn(disabled=True, width="medium"),
            "Kafka": st.column_config.TextColumn(disabled=True, width="large"),
            "Status": st.column_config.TextColumn(
                disabled=False,
                width="large"   # wide enough to avoid wrapping
            ),
        }
    )

    # Update only changed rows
    changed_rows = edited_app_df[edited_app_df["Status"] != app_df["Status"]]
    for i, row in changed_rows.iterrows():
        df.loc[app_df.loc[i, "index"], "Status"] = row["Status"]

# Save changes back to Excel
if st.button("Save Changes"):
    df.to_excel("KafkaReport.xlsx", index=False)
    st.success("Only edited rows saved to KafkaReport.xlsx!")