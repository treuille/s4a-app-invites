"""Wrapy PyGithub in Streamlit's caching functionality."""

import streamlit as st
import functools
import math
import time
import hashlib
from datetime import datetime
from github import Github
from github import NamedUser
from github import ContentFile
from github import RateLimitExceededException
from github import MainClass as GithubMainClass


def _get_attr_func(attr):
    """Returns a function which gets this attribute from an object."""
    def get_attr_func(obj):
        print(f'Getting {attr} from object of type {type(obj)}.')
        if attr == 'login':
            print('login: ' + obj.login)
        return getattr(obj, attr)
    return get_attr_func

def _hash_github_object(github):
    """Special hasher for the github function itself."""
    # Since we're hashing to desk, we'd don't want to store the raw
    # access token, instead we store a cryptographically secure (aka salted)
    # hash of it.
    hasher = hashlib.sha256()
    hasher.update(b'streamlit_salt')
    hasher.update(github._access_token.encode('utf-8'))
    print(github._access_token, '->', str(hasher.digest()))
    return hasher.digest()

_GITHUB_HASH_FUNCS = {
        GithubMainClass.Github: _hash_github_object, 
    NamedUser.NamedUser: _get_attr_func('login'),
    ContentFile.ContentFile: _get_attr_func('download_url'),
}

def rate_limit_search(func):
    """Function decorator to try to handle Github search rate limits.
    See: https://developer.github.com/v3/search/#rate-limit"""
    MAX_WAIT_SECONDS = 60.0

    @functools.wraps(func)
    def wrapped_func(github, *args, **kwargs):
        try:
            return func(github, *args, **kwargs)
        except RateLimitExceededException:
            # We were rate limited by Github, Figure out how long to wait.
            # Round up, and wait that long.
            search_limit = github.get_rate_limit().search
            remaining = search_limit.reset - datetime.utcnow()
            wait_seconds = math.ceil(remaining.total_seconds() + 1.0)
            wait_seconds = min(wait_seconds, MAX_WAIT_SECONDS)
            with st.spinner(f'Waiting {wait_seconds}s to avoid rate limit.'):
                time.sleep(wait_seconds)
            return func(github, *args, **kwargs)
    return wrapped_func

@st.cache(hash_funcs=_GITHUB_HASH_FUNCS)
def from_access_token(access_token):
    github = Github(access_token)
    github._access_token = access_token
    return github

@rate_limit_search
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

@rate_limit_search
@st.cache(hash_funcs=_GITHUB_HASH_FUNCS)
def get_streamlit_files(github, github_login):
    SEARCH_QUERY = 'extension:py "import streamlit as st" user:'
    files = github.search_code(SEARCH_QUERY + github_login)
    return list(files)

@st.cache(hash_funcs=_GITHUB_HASH_FUNCS, ttl=10)
def get_rate_limit(github):
    return github.get_rate_limit()
