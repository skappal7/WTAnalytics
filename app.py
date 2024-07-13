import streamlit as st
import pandas as pd
import json
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import nltk

nltk.download('stopwords')
nltk.download('punkt')

def clean_text(text, stop_words, exclude_words):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    words = word_tokenize(text)
    words = [word for word in words if word not in stop_words and word not in exclude_words and len(word) > 3]
    return words

def prepare_word_tree_data(data, stop_words, exclude_words, sentiment_filter, min_occurrences, max_occurrences):
    words_counter = Counter()

    filtered_data = data
    if sentiment_filter != 'All':
        sentiment_value = 1 if sentiment_filter == 'Positive' else -1
        filtered_data = data[data['sentiment'] == sentiment_value]

    for _, row in filtered_data.iterrows():
        words = clean_text(row['Review'], stop_words, exclude_words)
        for word in words:
            words_counter[word] += 1

    tree = {"name": "All Reviews", "children": []}
    labels = filtered_data['Label'].unique()

    for label in labels:
        label_node = {"name": label, "children": []}
        label_data = filtered_data[filtered_data['Label'] == label]
        categories = label_data['Category'].unique()

        for category in categories:
            category_node = {"name": category, "children": []}
            category_data = label_data[label_data['Category'] == category]

            words_counter = Counter()
            for _, row in category_data.iterrows():
                words = clean_text(row['Review'], stop_words, exclude_words)
                for word in words:
                    words_counter[word] += 1

            for word, count in words_counter.items():
                if min_occurrences <= count <= max_occurrences:
                    word_node = {"name": word, "size": count, "sentiment": 0}
                    for _, row in category_data.iterrows():
                        if word in clean_text(row['Review'], stop_words, exclude_words):
                            word_node["sentiment"] = row['sentiment']
                    category_node["children"].append(word_node)

            label_node["children"].append(category_node)
        tree["children"].append(label_node)

    return tree

def generate_word_tree_html(tree_data):
    with open("word_tree_template.html", "r") as template_file:
        html_template = template_file.read()

    html_output = html_template.replace("{data}", json.dumps(tree_data))
    return html_output

st.title("Word Tree Visualization")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

    stop_words = set(stopwords.words('english'))
    exclude_words = st.sidebar.text_input("Words to Exclude (comma separated)").split(',')
    sentiment_filter = st.sidebar.radio("Filter by Sentiment", ["All", "Positive", "Negative"])
    min_occurrences = st.sidebar.slider("Minimum Word Occurrences", 1, 10, 1)
    max_occurrences = st.sidebar.slider("Maximum Word Occurrences", 10, 100, 50)

    tree_data = prepare_word_tree_data(data, stop_words, exclude_words, sentiment_filter, min_occurrences, max_occurrences)
    html_output = generate_word_tree_html(tree_data)

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

    st.components.v1.html(html_output, height=600)
