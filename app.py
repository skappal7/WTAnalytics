import pandas as pd
import plotly.express as px
import streamlit as st

# Streamlit app
st.title("Interactive Sentiment Tree Map")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Color pickers in the sidebar
st.sidebar.header("Choose Sentiment Colors")
positive_color = st.sidebar.color_picker("Positive Sentiment Color", "#90EE90")  # lightgreen
negative_color = st.sidebar.color_picker("Negative Sentiment Color", "#F08080")  # lightcoral
neutral_color = st.sidebar.color_picker("Neutral Sentiment Color", "#D3D3D3")    # lightgray

if uploaded_file is not None:
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file)

    # Create hierarchical data structure for tree map
    fig = px.treemap(
        df,
        path=['Label', 'Category', 'sentiment_type'],
        values='sentiment',  # Assuming 'sentiment' is a numerical value for the size of each block
        color='sentiment_type',
        color_discrete_map={
            'Positive': positive_color,
            'Negative': negative_color,
            'Neutral': neutral_color
        },
        hover_data={'Review': True, 'sentiment': True}
    )

    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Please upload a CSV file to generate the tree map.")
