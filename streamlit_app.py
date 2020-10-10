import streamlit as st
import zipfile
import pandas as pd

"# S4A App Explorer"

def err(msg):
    """Print an error message to the user and stop."""
    st.warning(msg)
    st.stop()

raw_input = st.file_uploader('User list zip file.', types='zip')
if not raw_input:
    err('Please upload a user file. Ask TC for the file.')

@st.cache
def extract_user_table(raw_input):
    with zipfile.ZipFile(raw_input) as zip_input:
        names = zip_input.namelist()
        assert len(names) == 1 and names[0].endswith('.csv'), \
            "Zipfile must have only one csv."
        with zip_input.open(names[0]) as csv_input:
            return pd.read_csv(csv_input)

st.write(extract_user_table(raw_input))
