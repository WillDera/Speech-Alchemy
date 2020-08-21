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


directory = os.listdir('.')
filename = st.sidebar.selectbox(
    'Select a file',
    directory
)
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


# Here we get the texts from the results object then push them into the recognized text list
recognized_texts = []
for i in range(len(results["results"])):
    text = results["results"][i]["alternatives"][0]["transcript"]
    recognized_texts.append(text)


# here we merge all strs in the recognized_texts list into one big list.
recognized_text = " ".join(recognized_texts)


# Button to dump text extracted from the audio file
if st.button("Display extracted text"):
    st.success(recognized_text)


# Setting up the language translation feature
st.subheader("Language Translation")


# section to handle the language options
# create a language translator object
auth = IAMAuthenticator(lt_key)
lang_translator = LanguageTranslatorV3(
    version=lt_version, authenticator=auth)
lang_translator.set_service_url(url_lt)


@st.cache(suppress_st_warning=True)
def languages():
    # Create select box for the options
    languages = json_normalize(
        lang_translator.list_identifiable_languages().get_result(), "languages")
    return languages


st.write("Below are the language options you can select from.")
st.write(languages())

select_language = st.selectbox("Select language: ", languages())
st.write("You've selected: ", select_language)

model_id = "en-%s" % select_language
st.write(model_id)

if st.button("Convert to %s" % select_language):
    trans_response = lang_translator.translate(
        text=recognized_text, model_id=model_id)
    st.write(trans_response.result["translations"][0]["translation"])

# TODO: Test all languages to see which produce readable texts after translation
# TODO: limit the language options to only those that can produce readable texts
# TODO: Shift the language translation and text extraction parts to a different pages using st.sidebar functionality
