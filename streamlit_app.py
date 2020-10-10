import streamlit as st
import zipfile
import pandas as pd
from github import Github
from github import MainClass as GithubMainClass
import hashlib

"# S4A App Explorer"

# Utilities to hash the github class properly.

def hash_github_object(github):
    """Hashes the github object so that we can reuse it."""
    return github._access_token

MY_HASH_FUNCS = {GithubMainClass.Github: hash_github_object}

@st.cache(hash_funcs=MY_HASH_FUNCS)
def github_object_from_access_token(access_token):
    github = Github(access_token)
    github._access_token = access_token
    return github

@st.cache(hash_funcs=MY_HASH_FUNCS)
def get_user_from_email(github, email):
    """Returns a user for that email or None."""
    users = list(github.search_users(f'type:user {email} in:email'))
    if len(users) == 0:
        return None
    elif len(users) == 1:
        return users[0]
    else:
        raise RuntimeError(f'{email} associated with {len(users)} users.')

# Parsing the user's input

def err(msg):
    """Print an error message to the user and stop."""
    st.warning(msg)
    st.stop()

def get_config():
    """Returns all the config information to run the app."""
    
    # Get input
    config = st.sidebar.beta_expander('Config', expanded=True)
    raw_input = config.file_uploader('User list zip file.', types='zip')
    access_token = config.text_input("Github access token", type="password")

    # Check for input
    if not raw_input:
        err('Please upload a user file. Ask TC for the file.')
    if not access_token:
        err('Please enter a github access token.')

    # Parse and return the information
    user_table = extract_csv_from_zip_file(raw_input)
    github = github_object_from_access_token(access_token)
    return user_table, github

@st.cache
def extract_csv_from_zip_file(raw_input):
    with zipfile.ZipFile(raw_input) as zip_input:
        names = zip_input.namelist()
        assert len(names) == 1 and names[0].endswith('.csv'), \
            "Zipfile must have only one csv."
        with zip_input.open(names[0]) as csv_input:
            return pd.read_csv(csv_input)


user_table, github = get_config()
status = st.selectbox('Status', list(set(user_table['Status'])))
filtered_users = user_table[user_table['Status'] == status]
filtered_users = filtered_users.sort_values(by='Applied At', ascending=True)
filtered_users, len(filtered_users)
for s4a_user in filtered_users.itertuples():
    f'email: `{s4a_user.Email}`'
    github_user = get_user_from_email(github, s4a_user.Email)
    if not github_user:
        st.warning('Could not find ' + s4a_user.Email)
        continue
    f'twitter_username: `{github_user.twitter_username}`'
    f'created_at: `{github_user.created_at}`'
    f'name: `{github_user.name}`'
    f'login: `{github_user.login}`'
    raise RuntimeError('Stopping here.')

