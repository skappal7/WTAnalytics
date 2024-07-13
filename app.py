import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

# Function to convert CSV data to hierarchical JSON
def csv_to_json(data):
    tree = {"name": "All Reviews", "children": []}
    
    # Ensure columns are stripped of any leading/trailing spaces
    data.columns = data.columns.str.strip()
    
    # Check if required columns exist
    required_columns = ["Review", "Label", "Category", "sentiment", "sentiment_type"]
    for col in required_columns:
        if col not in data.columns:
            st.error(f"Missing required column: {col}")
            return None
    
    labels = data["Label"].unique()
    
    for label in labels:
        label_node = {"name": label, "children": []}
        label_data = data[data["Label"] == label]
        categories = label_data["Category"].unique()
        
        for category in categories:
            category_node = {"name": category, "children": []}
            category_data = label_data[label_data["Category"] == category]
            
            for _, row in category_data.iterrows():
                sentiment_color = {
                    "Negative": "lightcoral",
                    "Positive": "lightgreen",
                    "Neutral": "lightgrey"
                }[row["sentiment_type"]]
                
                review_node = {
                    "name": row["Review"],
                    "color": sentiment_color
                }
                
                category_node["children"].append(review_node)
            
            label_node["children"].append(category_node)
        
        tree["children"].append(label_node)
    
    return tree

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
    
    # Convert the data to hierarchical JSON format
    json_data = csv_to_json(data)
    
    if json_data:
        # Create the HTML template to embed the D3.js visualization
        html_template = open("d3_visualization.html").read()
        
        # Display the HTML template using Streamlit components
        components.html(html_template, height=800)
        
        # Send the data to the HTML file
        st.markdown(f"""
        <script>
            const data = {json.dumps(json_data)};
            window.parent.postMessage({{ type: "draw", data: data }}, "*");
        </script>
        """, unsafe_allow_html=True)
