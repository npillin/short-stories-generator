##################################
# Use simple password protection #
# to limit access to OpenAI API  #
# key used to power the app.     #
# Store password and API as      #
# Streamlit secret variables.    #
##################################

import hmac
import streamlit as st


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Mot de passe", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Mot de passe incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.



########################
# Packages and API key #
########################

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from openai import OpenAI

import os
os.environ['OPENAI_API_KEY'] = st.secrets["apikey"]



###################
# Langchain setup #
###################

llm = ChatOpenAI(model_name='gpt-4o')

# Story generation template
story_gen_template = """
You are a writer, specialized in writing short stories.
Your task is to write the following type of novel: {story_type}.
Make it approximately {n_words} words long.
Use the following structure: {structure}
"""
story_gen_prompt_template = PromptTemplate(
    input_variables=['story_type','n_words','structure'],
    template=story_gen_template
)

# Story translation template
story_transl_template = """
You are an exepert in translating short stories from english to other languages.
Your task if to translate a story from english to {story_lang}.
Here is the story to translate :
{story}
"""
story_transl_prompt_template = PromptTemplate(
    input_variables=['story_lang','story'],
    template=story_transl_template
)

# Setting up the LLM chains
story_gen_chain = LLMChain(llm=llm, prompt=story_gen_prompt_template, verbose=True)
story_transl_chain = LLMChain(llm=llm, prompt=story_transl_prompt_template, verbose=True)



#################
# App framework #
#################

st.title("Short Stories Generator")

# Type of story selector
story_type = st.selectbox(
    'Type of story',
    ('Adventure','Action','Thriller','Romance','Science fiction','Fantasy','Biography')
)

# Output languages (top 5 most spoken languages)
story_lang = st.selectbox(
    'In which language should the story be generated?',
    ('English','Mandarin','Hindi','Spanish','French')
)

# Structure
structure_default = """1. Exposition: introduce the character and the setting
2. Rising Action: the character faces a challenge or a crisis
3. Climax: the character is tested, most exciting part of the story
4. Falling Action: the character believes he has failed
5. Resolution: the character has actually succeded and has learned a valuable lesson
"""
with st.expander("Structure (adapt if needed)..."):
    structure = st.text_area(label="", value=structure_default, height=150)

# Length of the story
n_words = st.slider("How long (# of words) should the story be, approximatly?", 100, 2000, 300)

# Checkbox to enable or disable audio generation
gen_audio = st.checkbox("Generate audio version")

# Generate story
if st.button("Generate story"):
    # Call LLM chain to generate story
    story = story_gen_chain.run(story_type=story_type, n_words=n_words, structure=structure)
    # Should the story be translated?
    if story_lang != 'English':
         story = story_transl_chain.run(story_lang=story_lang, story=story)
    st.write(story)
    if gen_audio:
    # Generate audio version
        client = OpenAI()
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=story
            ) as response:
                response.stream_to_file('speech.mp3')
        st.audio('speech.mp3', format='audio/mpeg')
