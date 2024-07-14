import pandas as pd
import plotly.express as px
import streamlit as st

# Streamlit app configuration
st.set_page_config(page_title="Sentiment Tree Map", layout="wide")

# Custom CSS for modern look and feel using brand colors and fonts
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f5f5;
        padding: 20px;
    }
    .sidebar .sidebar-content {
        background-color: #e6e6e6;
    }
    .stButton>button {
        color: white;
        background-color: #0073e6;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        margin: 5px;
        font-family: 'Poppins', sans-serif;
    }
    .stTree > div {
        font-family: 'Poppins', sans-serif;
        color: #333;
    }
    .title-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .info-icon {
        font-size: 24px;
        color: #0073e6;
        cursor: pointer;
        margin-left: 10px;
        position: relative;
    }
    .tooltip {
        visibility: hidden;
        background-color: #555;
        color: #fff;
        text-align: left;
        border-radius: 5px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 150%; /* Position above the icon */
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.3s;
        font-family: 'Poppins', sans-serif;
        width: 220px;
        max-width: 300px;
        word-wrap: break-word;
    }
    .tooltip::after {
        content: "";
        position: absolute;
        top: 100%; /* Arrow at the bottom of the tooltip */
        left: 50%;
        transform: translateX(-50%);
        border-width: 5px;
        border-style: solid;
        border-color: #555 transparent transparent transparent;
    }
    .info-icon:hover .tooltip {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title and info icon
st.markdown(
    """
    <div class="title-container">
        <h1 style="font-family: 'Poppins', sans-serif; color: #333;">Interactive Sentiment Tree Map</h1>
        <span class="info-icon">
            ℹ️
            <div class="tooltip">
                <p>This app visualizes sentiment analysis data using a hierarchical tree map.</p>
                <p>Box sizes represent the frequency of occurrences, and colors indicate sentiment:</p>
                <ul style="text-align: left; margin: 0; padding: 0 0 0 20px;">
                    <li style="color: #90EE90;">Green: Positive</li>
                    <li style="color: #F08080;">Red: Negative</li>
                    <li style="color: #D3D3D3;">Gray: Neutral</li>
                </ul>
            </div>
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

# Move file uploader to the sidebar
st.sidebar.header("Upload your CSV file")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

# Color pickers in the sidebar
st.sidebar.header("Choose Sentiment Colors")
positive_color = st.sidebar.color_picker("Positive Sentiment Color", "#90EE90")  # lightgreen
negative_color = st.sidebar.color_picker("Negative Sentiment Color", "#F08080")  # lightcoral
neutral_color = st.sidebar.color_picker("Neutral Sentiment Color", "#D3D3D3")    # lightgray

# Radio buttons for filtering
sentiment_filter = st.sidebar.radio(
    "Select Sentiment Type",
    ('All', 'Positive', 'Negative', 'Neutral')
)

if uploaded_file is not None:
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file)

    # Preprocess data
    df.dropna(subset=['Label', 'Category', 'sentiment_type'], inplace=True)

    # Filter data based on sentiment type
    if sentiment_filter != 'All':
        df = df[df['sentiment_type'] == sentiment_filter]

    # Define paths for the tree map
    path = ['Label', 'Category', 'sentiment_type']
    color_col = 'sentiment_type'

    # Aggregate data to count occurrences
    aggregated_df = df.groupby(path).size().reset_index(name='counts')

    # Create hierarchical data structure for tree map
    try:
        fig = px.treemap(
            aggregated_df,
            path=path,
            values='counts',
            color=color_col,
            color_discrete_map={
                'Positive': positive_color,
                'Negative': negative_color,
                'Neutral': neutral_color
            },
            hover_data={'counts': True}
        )

        fig.update_layout(
            margin=dict(t=50, l=25, r=25, b=25),
            font=dict(family="Poppins", size=14, color='#333'),
            paper_bgcolor='#f5f5f5',
            plot_bgcolor='#f5f5f5'
        )

        st.plotly_chart(fig, use_container_width=True)
    except ValueError as e:
        st.error(f"ValueError: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.write("Please upload a CSV file to generate the tree map.")
