
import streamlit as st


st.title('My First Streamlit App')

st.write('Hello! This app is live on Streamlit Community Cloud.')


name = st.text_input('Enter your name:')

if name:

	st.write(f'Welcome, {name}!')