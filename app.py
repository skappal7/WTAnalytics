import pandas as pd
import plotly.express as px
import streamlit as st
from collections import Counter
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')

# Streamlit app
st.title("Interactive Sentiment Tree Map with Word Frequency Analysis")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

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
    # Drop rows with missing values in hierarchy columns
    df.dropna(subset=['Label', 'Category', 'sentiment_type'], inplace=True)

    # Filter data based on sentiment type
    if sentiment_filter != 'All':
        df = df[df['sentiment_type'] == sentiment_filter]

    # Aggregate data to count occurrences
    aggregated_df = df.groupby(['Label', 'Category', 'sentiment_type']).size().reset_index(name='counts')

    # Create hierarchical data structure for tree map
    try:
        fig = px.treemap(
            aggregated_df,
            path=['Label', 'Category', 'sentiment_type'],
            values='counts',  # Use counts as the size of each block
            color='sentiment_type',
            color_discrete_map={
                'Positive': positive_color,
                'Negative': negative_color,
                'Neutral': neutral_color
            },
            hover_data={'counts': True}
        )

        fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

        st.plotly_chart(fig, use_container_width=True)

        # Function to calculate word frequencies
        def calculate_word_frequencies(category):
            reviews = df[df['Category'] == category]['Review']
            words = word_tokenize(' '.join(reviews).lower())
            filtered_words = [word for word in words if word.isalnum() and word not in stopwords.words('english')]
            return Counter(filtered_words).most_common(10)

        # Display word frequencies for a selected category
        category_selected = st.selectbox("Select a Category to View Word Frequencies", df['Category'].unique())
        word_frequencies = calculate_word_frequencies(category_selected)

        if word_frequencies:
            words, counts = zip(*word_frequencies)
            plt.figure(figsize=(10, 6))
            plt.bar(words, counts, color='skyblue')
            plt.xlabel('Words')
            plt.ylabel('Counts')
            plt.title(f'Most Common Words in {category_selected}')
            st.pyplot(plt)
        else:
            st.write("No words to display for the selected category.")

    except ValueError as e:
        st.error(f"ValueError: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.write("Please upload a CSV file to generate the tree map.")
