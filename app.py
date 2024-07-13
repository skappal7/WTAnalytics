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
        # Display the D3.js visualization
        components.html("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>D3.js Visualization</title>
            <script src="https://d3js.org/d3.v6.min.js"></script>
            <style>
                body {
                    font-family: 'Poppins', sans-serif;
                }
                .bar {
                    fill: steelblue;
                }
                .bar:hover {
                    fill: orange;
                }
                .axis-label {
                    font: 12px sans-serif;
                }
                .dendrogram-node circle {
                    fill: #999;
                }
                .dendrogram-node text {
                    font: 10px sans-serif;
                }
                .dendrogram-link {
                    fill: none;
                    stroke: #555;
                    stroke-width: 1.5px;
                }
            </style>
        </head>
        <body>
            <div id="dendrogram"></div>
            <script>
                function drawVisualization(data) {
                    const margin = {top: 20, right: 90, bottom: 30, left: 90},
                        width = 960 - margin.left - margin.right,
                        height = 500 - margin.top - margin.bottom;

                    const svg = d3.select("#dendrogram").append("svg")
                        .attr("width", width + margin.left + margin.right)
                        .attr("height", height + margin.top + margin.bottom)
                        .append("g")
                        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

                    const root = d3.hierarchy(data);

                    const treeLayout = d3.tree().size([height, width]);

                    treeLayout(root);

                    svg.selectAll('.link')
                        .data(root.links())
                        .enter()
                        .append('path')
                        .attr('class', 'dendrogram-link')
                        .attr('d', d3.linkHorizontal()
                            .x(d => d.y)
                            .y(d => d.x));

                    const node = svg.selectAll('.dendrogram-node')
                        .data(root.descendants())
                        .enter()
                        .append('g')
                        .attr('class', 'dendrogram-node')
                        .attr('transform', d => `translate(${d.y},${d.x})`)
                        .on('click', function(event, d) {
                            d.children = d.children ? null : d._children;
                            drawVisualization(data);
                        });

                    node.append('circle')
                        .attr('r', 5);

                    node.append('text')
                        .attr('dy', '.35em')
                        .attr('x', d => d.children ? -13 : 13)
                        .style('text-anchor', d => d.children ? 'end' : 'start')
                        .text(d => d.data.name);
                }

                window.addEventListener("message", (event) => {
                    if (event.data.type === "draw") {
                        drawVisualization(event.data.data);
                    }
                });

                const data = """ + json.dumps(json_data) + """;
                window.parent.postMessage({ type: "draw", data: data }, "*");
            </script>
        </body>
        </html>
        """, height=800)
