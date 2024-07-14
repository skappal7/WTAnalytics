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
    .info-box {
        background-color: #f9f9f9; /* Very light grey */
        color: #333;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        font-family: 'Poppins', sans-serif;
        margin-bottom: 20px;
        font-size: 14px; /* Reduced font size */
    }
    .info-box ul {
        list-style-type: none;
        padding-left: 0;
    }
    .info-box li::before {
        content: "•";
        color: #333;
        display: inline-block; 
        width: 1em;
        margin-left: -1em;
    }
    .stTree > div {
        font-family: 'Poppins', sans-serif;
        color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown(
    """
    <div class="title-container">
        <h1 style="font-family: 'Poppins', sans-serif; color: #333;">Interactive Sentiment Tree Map</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Collapsible info box
with st.expander("ⓘ Information about this visualization"):
    st.markdown(
        """
        <div class="info-box">
            <p>This interactive web application provides a powerful and intuitive tool for visualizing sentiment analysis data. It's designed to help users quickly grasp complex patterns and distributions within their sentiment data through an easy-to-understand hierarchical tree map.</p>
            <p>This application serves as a valuable asset for anyone working with sentiment analysis data, offering a blend of powerful visualization capabilities and user-friendly design. It transforms complex datasets into actionable insights, enabling users to make data-driven decisions more efficiently.</p>
            <p>Box sizes represent the frequency of occurrences, and colors indicate sentiment:</p>
            <ul>
                <li style="color: #07B1FC;">Blue: Positive</li>
                <li style="color: #FAAF3B;">Yellow: Negative</li>
                <li style="color: #979797;">Gray: Neutral</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

# Move file uploader to the sidebar
st.sidebar.header("Upload your CSV file")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

# Color pickers in the sidebar
st.sidebar.header("Choose Sentiment Colors")
positive_color = st.sidebar.color_picker("Positive Sentiment Color", "#07B1FC")  # bright blue
negative_color = st.sidebar.color_picker("Negative Sentiment Color", "#FAAF3B")  # yellow
neutral_color = st.sidebar.color_picker("Neutral Sentiment Color", "#979797")    # light gray

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

        fig.update_traces(
            texttemplate='<b>%{label}<br>%{value}</b>',
            textfont=dict(family="Poppins", color="white", size=20)  # Ensure font is Poppins and adjust size to fit your preference
        )

        fig.update_layout(
            margin=dict(t=50, l=25, r=25, b=25),
            font=dict(family="Poppins", size=14, color='#333'),
            paper_bgcolor='#f5f5f5',
            plot_bgcolor='#f5f5f5',
            treemapcolorway=["#06516F", "#0098DB", "#FAAF3B", "#333333", "#979797"]
        )

        st.plotly_chart(fig, use_container_width=True)
    except ValueError as e:
        st.error(f"ValueError: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.write("Please upload a CSV file to generate the tree map.")
