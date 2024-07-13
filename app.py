import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

# Set up the Streamlit app structure
st.title("Sentiment Analysis Visualization with D3.js")

# File upload component
uploaded_file = st.file_uploader("Upload your sentiment CSV file", type="csv")

if uploaded_file:
    # Read the CSV file
    data = pd.read_csv(uploaded_file)
    
    # Display the uploaded data
    st.write("Uploaded Data")
    st.dataframe(data)
    
    # Convert the data to JSON format
    json_data = data.to_json(orient='records')
    
    # Create the HTML template to embed the D3.js visualization
    html_template = open("d3_visualization.html").read()
    
    # Display the HTML template using Streamlit components
    components.html(html_template, height=800)
    
    # Send the data to the HTML file
    components.iframe(src="about:blank", width=0, height=0)
    st.markdown(f"""
    <script>
        const data = {json_data};
        window.parent.postMessage({{ type: "draw", data: data }}, "*");
    </script>
    """, unsafe_allow_html=True)
