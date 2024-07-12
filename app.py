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

def get_related_words(word, data, stop_words, exclude_words, max_related=5):
    related_words = Counter()
    sentiment_sum = 0
    reviews_count = 0
    
    for _, row in data.iterrows():
        words = clean_text(row['Review'], stop_words, exclude_words)
        if word in words:
            related_words.update(words)
            sentiment_sum += row['sentiment']
            reviews_count += 1
    
    related_words.pop(word, None)  # Remove the word itself from related words
    
    avg_sentiment = sentiment_sum / reviews_count if reviews_count > 0 else 0
    
    return [
        {
            "name": w,
            "size": c,
            "sentiment": avg_sentiment,
            "label": f"Related to '{word}'",
            "category": "Related Word"
        } for w, c in related_words.most_common(max_related)
    ]

def prepare_initial_tree(data, stop_words, exclude_words, min_occurrences=10):
    words_counter = Counter()
    
    for _, row in data.iterrows():
        words = clean_text(row['Review'], stop_words, exclude_words)
        words_counter.update(words)
    
    root = {"name": "Reviews", "children": []}
    for word, count in words_counter.most_common(10):  # Start with top 10 words
        if count >= min_occurrences:
            word_node = {
                "name": word,
                "size": count,
                "sentiment": 0,  # You might want to calculate this
                "label": "Top Word",
                "category": "Initial Word"
            }
            root["children"].append(word_node)
    
    return root

st.title("Word Tree Visualization")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

    stop_words = set(stopwords.words('english'))
    exclude_words = st.sidebar.text_input("Words to Exclude (comma separated)").split(',')
    
    initial_tree = prepare_initial_tree(data, stop_words, exclude_words)
    
    st.session_state['tree_data'] = initial_tree
    st.session_state['data'] = data
    st.session_state['stop_words'] = stop_words
    st.session_state['exclude_words'] = exclude_words

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

    # Placeholder for D3.js visualization
    st.components.v1.html("""
    <div id="wordTree"></div>
    <script src="https://d3js.org/d3.v5.min.js"></script>
    <script>
        // D3.js code will go here
    </script>
    """, height=600)

    # Get Related Words functionality
    st.subheader("Get Related Words")
    word = st.text_input("Enter a word:")
    if st.button('Get Related Words') and word:
        related = get_related_words(word, data, stop_words, exclude_words)
        st.write(related)

    # Add this to your Streamlit app to handle AJAX requests
    if st.button('Update Tree'):
        st.write("Tree updated")  # This is a placeholder, actual updating will be done in JS
