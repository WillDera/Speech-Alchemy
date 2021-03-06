import streamlit as st
import pandas as pd
from decouple import config
import os
from ibm_watson import SpeechToTextV1, LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json
from pandas.io.json import json_normalize  # deprecated


# Reading the dataset
@st.cache
def get_data():
    return pd.read_csv('language_names_and_codes.csv')


df = get_data()

# env configurations
url_s2t = config('URL_S2T')
api_key = config('API_KEY')
url_lt = config('URL_LT')
lt_key = config('LT_KEY')
lt_version = config('LT_VERSION')


# Introduction
st.write(
    """
        # My Speech Alchemist
        
        This application allows you to extract the text from an audio file and then convert it to text in nealry any language.
        
        ## Text Extractor
    """
)


# Sidebar
st.sidebar.title("Speech Alchemy")
directory = os.listdir('.')
filename = st.sidebar.selectbox(
    'Select a file',
    directory
)


# ------------------------ Text Extraction ---------------------------- #


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
st.write("The table below shows you the extracted text and confidence of the model from `%s`" % filename)
st.write("You can hover on any of the transcripts to see a preview of the full text")
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


# ------------------------ Language Translation ---------------------------- #
st.subheader("Language Translation")


# create a language translator object
auth = IAMAuthenticator(lt_key)
lang_translator = LanguageTranslatorV3(
    version=lt_version, authenticator=auth)
lang_translator.set_service_url(url_lt)


st.sidebar.markdown("Below are the language options you can select from.")
st.sidebar.table(df)


# ------------------------ Display user options for language to be translated to. ------------------------ #
# created a list from the dataset "Language Name" column
languages_names = [i for i in df["Language Name"]]
select_language = st.selectbox("Select language: ", languages_names)


# ------------------------ set the model_id, from english to the selected language ------------------------ #
# get index of selected option from the "Language Name" list
index = languages_names.index(select_language)
# create a list from the dataset "Language Code" column
languages_codes = [j for j in df["Language Code"]]
# setting the id to the corresponding value of the Language code using the Language Name location
id = languages_codes[index]
model_id = "en-%s" % id

if st.button("Convert to %s" % select_language):
    trans_response = lang_translator.translate(
        text=recognized_text, model_id=model_id)
    st.write(trans_response.result["translations"][0]["translation"])
