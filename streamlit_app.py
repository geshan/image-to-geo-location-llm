import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

import os

st.set_page_config(page_title="Photo to Geo location guesser",
                   page_icon="📍",
                   layout="wide",
                   initial_sidebar_state="expanded")

st.header("Guess location from image")

with st.sidebar:
    st.header("Location guessing app")
    st.write("This app uses an LLM (Gemini) to take the image as input and guess the geo location for the provided photo.")
    st.header("How to use this app")
    st.write("1. Upload a photo - jpg only (less than 3 MB)")
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
        PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
        LOCATION = os.environ.get("GOOGLE_CLOUD_REGION")

        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )

        text1 = types.Part.from_text(text="""You are an OSINT investigator. Your job is to geolocate where the photos are taken. Provide the country, region, and city name of the location. Please pinpoint the exact location with latitude and longitude where the photo was taken.  

        Could you always explain your methodology and how you concluded? Provide steps to verify your work. Also, mention the percentage of how sure you are of the place you have identified it to be and add a Google Maps link to the exact location.""")
        image1 = types.Part.from_bytes(
            data=bytes_data,
            mime_type="image/jpeg"
        )

        model = "gemini-2.0-flash-lite-001"
        contents = [
            types.Content(
            role="user",
            parts=[
                text1,
                image1
            ]
            )
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature = 0.1,
            top_p = 0.5,
            max_output_tokens = 4096,
            response_modalities = ["TEXT"],
            safety_settings = [types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="OFF"
            ),types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="OFF"
            ),types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="OFF"
            ),types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="OFF"
            )],
        )
    
        for chunk in client.models.generate_content_stream(
            model = model,
            contents = contents,
            config = generate_content_config,
            ):
            st.write(chunk.text)
