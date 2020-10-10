"""Wrapy PyGithub in Streamlit's caching functionality."""

import streamlit as st

from github import Github
from github import NamedUser
from github import MainClass as GithubMainClass

def _get_attr_func(attr):
    """Returns a function which gets this attribute from an object."""
    def get_attr_func(obj):
        print(f'Getting {attr} from object of type {type(obj)}.')
        if attr == 'login':
            print('login: ' + obj.login)
        return getattr(obj, attr)
    return get_attr_func

_GITHUB_HASH_FUNCS = {
    GithubMainClass.Github: _get_attr_func('_access_token'),
    NamedUser.NamedUser: _get_attr_func('login'),
}

@st.cache(hash_funcs=_GITHUB_HASH_FUNCS)
def from_access_token(access_token):
    github = Github(access_token)
    github._access_token = access_token
    return github

@st.cache(hash_funcs=_GITHUB_HASH_FUNCS)
def get_user_from_email(github, email):
    """Returns a user for that email or None."""
    users = list(github.search_users(f'type:user {email} in:email'))
    if len(users) == 0:
        return None
    elif len(users) == 1:
        return users[0]
    else:
        raise RuntimeError(f'{email} associated with {len(users)} users.')

@st.cache(hash_funcs=_GITHUB_HASH_FUNCS)
def get_streamlit_files(github, github_login):
    SEARCH_QUERY = 'extension:py "import streamlit as st" user:'
    files = github.search_code(SEARCH_QUERY + github_login)
    return list(files)


