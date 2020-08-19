import streamlit as st
from decouple import config
import datetime
import time
import os

# importing modules for watson
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json
from pandas.io.json import json_normalize

# Introduction Header
st.title("Speech to Text")

# Introductory text
st.markdown(
    "This application allows you to send in an audio file and the convert it to text in nealry any language")

url_s2t = config('URL_S2T')
api_key = config('API_KEY')


def file_selector(folder_path='.'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a file', filenames)
    return os.path.join(folder_path, selected_filename)


filename = file_selector()
st.write('You selected `%s`' % filename)


# Creating a speech to text Object
@st.cache
def s2t_object():
    auth = IAMAuthenticator(api_key)
    speech2text = SpeechToTextV1(authenticator=auth)
    speech2text.set_service_url(url_s2t)

    with open(filename, mode='rb') as wav:
        response = speech2text.recognize(audio=wav, content_type='audio/mp3')
        return response.result


results = s2t_object()
# st.write(results)
st.write(json_normalize(response.result['results'], "alternatives"))
