import streamlit as st
from decouple import config
import datetime
import time
import os

# importing modules for watson
from ibm_watson import SpeechToTextV1, LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json
from pandas.io.json import json_normalize  # deprecated
# from pandas.json_normalize import json_normalize

# Introduction Header
st.title("Speech to Text")

# Introductory text
st.markdown(
    "This application allows you to send in an audio file and the convert it to text in nealry any language")

url_s2t = config('URL_S2T')
api_key = config('API_KEY')
url_lt = config('URL_LT')
lt_key = config('LT_KEY')
lt_version = config('LT_VERSION')


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
# st.write(results["results"])
# [0]["alternatives"][0]["transcript"]
st.write(json_normalize(results['results'], "alternatives"))


# Setting up the language translation feature
st.subheader("Language Translation")


@st.cache(suppress_st_warning=True)
def languages():
    # create a language translator object
    auth = IAMAuthenticator(lt_key)
    lang_translator = LanguageTranslatorV3(
        version=lt_version, authenticator=auth)
    lang_translator.set_service_url(url_lt)

    # Create select box for the options
    languages = json_normalize(
        lang_translator.list_identifiable_languages().get_result(), "languages")
    select_language = st.selectbox("Select language: ", languages)
    return select_language


selected_language = languages()
st.write(selected_language)
