import cached_github
import streamlit as st
import pandas as pd
import zipfile
import os

"# S4A App Explorer"

# Parsing the user's input

def err(msg):
    """Print an error message to the user and stop."""
    st.warning(msg)
    st.stop()

def get_config():
    """Returns all the config information to run the app."""
    
    # Get input
    zip_file = get_zip_file()
    access_token = st.sidebar.text_input("Github access token", type="password")

    # Check for input
    if not zip_file:
        err('Please upload a user file. Ask TC for the file.')
    if not access_token:
        err('Please enter a github access token.')

    # Parse and return the information
    user_table = extract_csv_from_zip_file(zip_file)
    github = cached_github.from_access_token(access_token)
    return user_table, github

def get_zip_file():
    """Return a zip file object, either from the current directory or uploaded."""
    # This is a sentinal to indicate that we upload a file if either the user
    # selects to upload manually or if there are no zip files in the current
    # directory.
    UPLOAD_FILE = "Upload a zip file"

    # First try to upload a file from the current directory.
    zip_filenames = [f for f in os.listdir('.') if f.endswith('.zip')]
    if zip_filenames:
        # Even if there are local files, give the option to upload.
        zip_filenames = [UPLOAD_FILE] + zip_filenames
        zip_filename = st.sidebar.selectbox('Select zip file', zip_filenames)
    else:
        # If no local zip files, then you must upload.
        zip_filename = UPLOAD_FILE

    # Now open the file, either locally or with an uploader.
    if zip_filename == UPLOAD_FILE:
        zip_file = st.sidebar.file_uploader('User list zip file.', types='zip')
    else:
        zip_file = open(zip_filename, 'rb')
    return zip_file

# @st.cache
def extract_csv_from_zip_file(zip_file):
    with zipfile.ZipFile(zip_file) as zip_input:
        names = zip_input.namelist()
        assert len(names) == 1 and names[0].endswith('.csv'), \
            "Zipfile must have only one csv."
        with zip_input.open(names[0]) as csv_input:
            return pd.read_csv(csv_input)


user_table, github = get_config()
# f'rate_limit {type(rate_limit)}
# st.write(rate_limit)
# st.write(dir(rate_limit))
# st.write(rate_limit.raw_headers)
# st.write('search_limit', type(search_limit))
# st.write(dir(search_limit))
# f'remaining: `{search_limit.remaining}`'
# raise RuntimeError('Stop here.')

status = st.selectbox('Status', list(set(user_table['Status'])))
filtered_users = user_table[user_table['Status'] == status]
filtered_users = filtered_users.sort_values(by='Applied At', ascending=True)
filtered_users, len(filtered_users)
results = {'email': [], 'login': [], 'streamlit_files': []}
MAX_ITER = st.slider('Max iterations', 1, 3000, 1)
st.success(f'Will halt after `{MAX_ITER}` iterations.')
for i, s4a_user in enumerate(filtered_users.itertuples()):
    if i >= MAX_ITER:
        break
    s4a_email = s4a_user.Email 
    github_user = cached_github.get_user_from_email(github, s4a_email)
    f'### {i}'
    f'`{s4a_user.Email}` -> `{github_user}`'
    if not github_user:
        continue
    github_login = github_user.login
    f'twitter_username: `{github_user.twitter_username}`'
    f'created_at: `{github_user.created_at}`'
    f'name: `{github_user.name}`'
    f'login: `{github_login}`'
    files = cached_github.get_streamlit_files(github, github_login)
    if len(files) > 1000:
        st.write(files)
        st.write(files[0].download_url)
        raise RuntimeError('Checking types.')
    f'num files: `{len(files)}`'
    results['email'].append(s4a_email)
    results['login'].append(github_login)
    results['streamlit_files'].append(len(files))
st.write(pd.DataFrame(results))
