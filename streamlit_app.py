import streamlit as st
import zipfile
import pandas as pd

"# S4A App Explorer"

def err(msg):
    """Print an error message to the user and stop."""
    st.warning(msg)
    st.stop()

def get_config():
    """Returns all the config information to run the app."""
    config = st.sidebar.beta_expander('Config', expanded=True)
    raw_input = config.file_uploader('User list zip file.', types='zip')
    if not raw_input:
        err('Please upload a user file. Ask TC for the file.')
    return raw_input

@st.cache
def extract_csv_from_zip_file(raw_input):
    with zipfile.ZipFile(raw_input) as zip_input:
        names = zip_input.namelist()
        assert len(names) == 1 and names[0].endswith('.csv'), \
            "Zipfile must have only one csv."
        with zip_input.open(names[0]) as csv_input:
            return pd.read_csv(csv_input)

raw_input = get_config()
user_table = extract_csv_from_zip_file(raw_input)
status = st.selectbox('Status', list(set(user_table['Status'])))
filtered_users = user_table[user_table['Status'] == status]
filtered_users = filtered_users.sort_values(by='Applied At', ascending=True)
filtered_users, len(filtered_users)
for user in filtered_users.itertuples():
    st.write(dir(user))
    # st.text(user)
    # st.text(type(user))
    break
