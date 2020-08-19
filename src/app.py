import streamlit as st
import datetime
import time
import os

# importing modules for watson
from ibm_watson import SpeechToTextV1
import json
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Introduction Header
st.title("Speech to Text")

# Introductory text
st.markdown(
    "This application allows you to send in an audio file and the convert it to text in nealry any language")


def file_selector(folder_path='.'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a file', filenames)
    return os.path.join(folder_path, selected_filename)


filename = file_selector()
st.write('You selected `%s`' % filename)
