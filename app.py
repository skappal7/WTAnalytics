import streamlit as st
import pandas as pd
import json
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import nltk

nltk.download('stopwords')

# Function to clean and process text
def clean_text(text, stop_words, exclude_words):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    words = word_tokenize(text)
    words = [word for word in words if word not in stop_words and word not in exclude_words and len(word) > 3]
    return words

# Function to prepare hierarchical data for D3.js
def prepare_word_tree_data(data, stop_words, exclude_words, sentiment_filter, min_occurrences, max_occurrences):
    words_counter = Counter()

    filtered_data = data
    if sentiment_filter != 'All':
        sentiment_value = 1 if sentiment_filter == 'Positive' else -1
        filtered_data = data[data['sentiment'] == sentiment_value]

    for _, row in filtered_data.iterrows():
        words = clean_text(row['Review'], stop_words, exclude_words)
        words_counter.update(words)

    tree = {"name": "root", "children": []}
    for word, count in words_counter.items():
        if min_occurrences <= count <= max_occurrences:
            current_level = tree
            for char in word:
                match = next((child for child in current_level["children"] if child["name"] == char), None)
                if match:
                    current_level = match
                else:
                    new_node = {"name": char, "children": []}
                    current_level["children"].append(new_node)
                    current_level = new_node
            current_level["size"] = count

    return tree

# Function to generate the HTML for the word tree
def generate_word_tree_html(tree_data):
    with open("word_tree_template.html", "r") as template_file:
        html_template = template_file.read()

    html_output = html_template.replace("{data}", json.dumps(tree_data))
    return html_output

# Streamlit app
st.title("Word Tree Visualization")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

    stop_words = set(stopwords.words('english'))
    exclude_words = st.text_input("Words to Exclude (comma separated)").split(',')
    sentiment_filter = st.selectbox("Filter by Sentiment", ["All", "Positive", "Negative"])
    min_occurrences = st.slider("Minimum Word Occurrences", 1, 10, 1)
    max_occurrences = st.slider("Maximum Word Occurrences", 10, 100, 50)

    tree_data = prepare_word_tree_data(data, stop_words, exclude_words, sentiment_filter, min_occurrences, max_occurrences)
    html_output = generate_word_tree_html(tree_data)

    st.components.v1.html(html_output, height=600)
