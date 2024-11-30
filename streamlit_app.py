import streamlit as st
from PIL import Image
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
import time

st.set_page_config(page_title="Photo to Geo location guesser",
                   page_icon="📍",
                   layout="centered",
                   initial_sidebar_state="expanded")

st.header("Guess location from image")

with st.sidebar:
    st.header("Location guessing app")
    st.write("This app uses an LLM (Gemini) to take the image as input and guess the geo location for the provided photo.")
    st.header("How to use this app")
    st.write("1. Uplaod a photo - jpg only (less than 2 MB)")
    st.write("2. Scroll down and click 'Guess the location!' button")
    st.write("3. Wait for a bit, it will show the output below the button")

uploaded_file = st.file_uploader("Choose an Image file", accept_multiple_files=False, type=['jpg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    st.image(image, caption='Uploaded Image', use_container_width=True)
    bytes_data = uploaded_file.getvalue()

    generate = st.button("Guess the location!", type="primary", use_container_width=True)

    if generate:
        st.write("let's guess the location now")
        text1 = """You are an OSINT investigator. Your job is to geolocate where photos are taken. Provide the country, region, and city name of the location. If possible, pinpoint the exact location with latitude and longitude of where the photo was taken.  
        
            Always explain your methodology and how you came to the conclusion. Provide steps to verify your work also mention the percentage of how sure you are of the place you have identified it to be."""
        image1 = Part.from_data(
            mime_type="image/jpeg",
            data=bytes_data)

        generation_config = {
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
        }

        safety_settings = [
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=SafetySetting.HarmBlockThreshold.OFF
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=SafetySetting.HarmBlockThreshold.OFF
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=SafetySetting.HarmBlockThreshold.OFF
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=SafetySetting.HarmBlockThreshold.OFF
            ),
        ]

        vertexai.init(project="test-proj-219922", location="us-central1")
        model = GenerativeModel(
            "gemini-1.5-pro-002",
        )
        responses = model.generate_content(
            [text1, image1],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True,
        )

        for response in responses:
            st.write(response.text)
