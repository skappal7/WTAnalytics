import streamlit as st
import pandas as pd
import json
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from collections import Counter
import nltk

# Download required NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# Function to clean and process text
def clean_text(text, stop_words, exclude_words, n):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    words = word_tokenize(text)
    words = [word for word in words if word not in stop_words and word not in exclude_words and len(word) > 3]
    phrases = [' '.join(gram) for gram in ngrams(words, n)]
    return phrases

# Function to prepare hierarchical data for D3.js
def prepare_word_tree_data(data, stop_words, exclude_words, sentiment_filter, min_occurrences, max_occurrences, n):
    words_counter = Counter()

    filtered_data = data
    if sentiment_filter != 'All':
        sentiment_value = 1 if sentiment_filter == 'Positive' else -1
        filtered_data = data[data['sentiment'] == sentiment_value]

    for _, row in filtered_data.iterrows():
        phrases = clean_text(row['Review'], stop_words, exclude_words, n)
        for phrase in phrases:
            words_counter[phrase] += 1

    def add_to_tree(tree, phrase, count, sentiment):
        parts = phrase.split()
        current_level = tree
        for i, part in enumerate(parts):
            found = False
            for child in current_level["children"]:
                if child["name"] == part:
                    current_level = child
                    found = True
                    break
            if not found:
                new_child = {"name": part, "children": [], "sentiment": sentiment}
                if i == len(parts) - 1:  # If it's the last part
                    new_child["size"] = count
                current_level["children"].append(new_child)
                current_level = new_child

    tree = {"name": "All Reviews", "children": [], "sentiment": 0}
    for phrase, count in words_counter.items():
        if min_occurrences <= count <= max_occurrences:
            sentiment = sum(row['sentiment'] for _, row in filtered_data.iterrows() 
                            if phrase in clean_text(row['Review'], stop_words, exclude_words, n))
            sentiment = sentiment / count  # Average sentiment
            add_to_tree(tree, phrase, count, sentiment)

    return tree

# Function to generate the HTML for the word tree
def generate_word_tree_html(tree_data):
    with open("word_tree_template.html", "r") as template_file:
        html_template = template_file.read()

    # Convert tree_data to JSON
    tree_data_json = json.dumps(tree_data)

    # Replace the placeholder in the template with the actual data
    html_output = html_template.replace('var treeData = {data};', f'var treeData = {tree_data_json};')

    return html_output

# Streamlit app
def main():
    st.title("Word Tree Visualization")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        stop_words = set(stopwords.words('english'))
        exclude_words = st.sidebar.text_input("Words to Exclude (comma separated)").split(',')
        sentiment_filter = st.sidebar.radio("Filter by Sentiment", ["All", "Positive", "Negative"])
        min_occurrences = st.sidebar.slider("Minimum Word Occurrences", 1, 10, 1)
        max_occurrences = st.sidebar.slider("Maximum Word Occurrences", 10, 100, 50)
        n = st.sidebar.slider("N-grams (number of words in phrases)", 2, 3, 2)

        tree_data = prepare_word_tree_data(data, stop_words, exclude_words, sentiment_filter, min_occurrences, max_occurrences, n)
        html_output = generate_word_tree_html(tree_data)

        # Display review counts
        total_reviews = len(data)
        positive_reviews = len(data[data['sentiment'] > 0])
        negative_reviews = len(data[data['sentiment'] < 0])
        neutral_reviews = len(data[data['sentiment'] == 0])
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
            <div style="border: 1px solid #ccc; padding: 10px; border-radius: 10px;">
                <strong>Total Reviews</strong><br>{total_reviews}
            </div>
            <div style="border: 1px solid #ccc; padding: 10px; border-radius: 10px;">
                <strong>Positive Reviews</strong><br>{positive_reviews}
            </div>
            <div style="border: 1px solid #ccc; padding: 10px; border-radius: 10px;">
                <strong>Negative Reviews</strong><br>{negative_reviews}
            </div>
            <div style="border: 1px solid #ccc; padding: 10px; border-radius: 10px;">
                <strong>Neutral Reviews</strong><br>{neutral_reviews}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.components.v1.html(html_output, height=800)

if __name__ == "__main__":
    main()
