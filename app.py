import streamlit as st
import pandas as pd
import json

def prepare_word_tree_data(data):
    tree = {"name": "root", "children": []}
    for _, row in data.iterrows():
        review = row['Review']
        words = review.split()
        current_level = tree
        for word in words:
            match = next((child for child in current_level["children"] if child["name"] == word), None)
            if match:
                current_level = match
            else:
                new_node = {"name": word, "children": []}
                current_level["children"].append(new_node)
                current_level = new_node
        current_level["label"] = row['Label']
        current_level["category"] = row['Category']
        current_level["sentiment"] = row['sentiment']
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
    tree_data = prepare_word_tree_data(data)
    html_output = generate_word_tree_html(tree_data)
    st.components.v1.html(html_output, height=600)
