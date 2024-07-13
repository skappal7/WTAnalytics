import streamlit as st
import pandas as pd
import json
import os

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
    
    # Save the data to a JSON file to be used by D3.js
    json_data = data.to_json(orient='records')
    with open('data.json', 'w') as f:
        f.write(json_data)
    
    # HTML template to embed the D3.js visualization
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>D3.js Visualization</title>
        <script src="https://d3js.org/d3.v6.min.js"></script>
        <style>
            .bar {{
                fill: steelblue;
            }}
            .bar:hover {{
                fill: orange;
            }}
            .axis-label {{
                font: 12px sans-serif;
            }}
            .dendrogram-node circle {{
                fill: #999;
            }}
            .dendrogram-node text {{
                font: 10px sans-serif;
            }}
            .dendrogram-link {{
                fill: none;
                stroke: #555;
                stroke-width: 1.5px;
            }}
        </style>
    </head>
    <body>
        <div id="dendrogram"></div>
        <div id="barchart"></div>
        <script>
            // Load the data
            d3.json('data.json').then(data => {{
                // Process the data for the dendrogram
                const root = d3.stratify()
                    .id(d => d.category)
                    .parentId(d => d.label)(data)
                    .sum(d => d.value)
                    .sort((a, b) => b.height - a.height || b.value - a.value);
    
                // Create the dendrogram
                const dendrogram = d3.tree().size([800, 400]);
                const svgDendrogram = d3.select("#dendrogram").append("svg")
                    .attr("width", 960)
                    .attr("height", 500)
                    .append("g")
                    .attr("transform", "translate(40,0)");
    
                const link = svgDendrogram.selectAll(".dendrogram-link")
                    .data(dendrogram(root).links())
                    .enter().append("path")
                    .attr("class", "dendrogram-link")
                    .attr("d", d3.linkHorizontal()
                        .x(d => d.y)
                        .y(d => d.x));
    
                const node = svgDendrogram.selectAll(".dendrogram-node")
                    .data(root.descendants())
                    .enter().append("g")
                    .attr("class", "dendrogram-node")
                    .attr("transform", d => `translate(${d.y},${d.x})`);
    
                node.append("circle")
                    .attr("r", 2.5);
    
                node.append("text")
                    .attr("dy", 3)
                    .attr("x", d => d.children ? -8 : 8)
                    .style("text-anchor", d => d.children ? "end" : "start")
                    .text(d => d.data.name);
    
                // Process the data for the bar chart
                const sentimentColors = {{
                    'Negative': 'lightcoral',
                    'Positive': 'lightgreen',
                    'Neutral': 'lightgrey'
                }};
    
                const groupedData = d3.groups(data, d => d.label, d => d.category, d => d.sentiment);
    
                // Create the bar chart
                const margin = {{ top: 20, right: 30, bottom: 40, left: 90 }};
                const width = 960 - margin.left - margin.right;
                const height = 500 - margin.top - margin.bottom;
    
                const svgBarChart = d3.select("#barchart").append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform", `translate(${margin.left},${margin.top})`);
    
                const x = d3.scaleLinear()
                    .range([0, width])
                    .domain([0, d3.max(groupedData, d => d3.max(d[1], d => d3.max(d[1], d => d3.max(d[1], d => d.value))))]);
    
                const y = d3.scaleBand()
                    .range([height, 0])
                    .padding(0.1)
                    .domain(groupedData.map(d => d[0]));
    
                svgBarChart.append("g")
                    .call(d3.axisLeft(y).tickSize(0))
                    .selectAll("text")
                    .attr("class", "axis-label");
    
                svgBarChart.selectAll(".bar")
                    .data(groupedData)
                    .enter().append("rect")
                    .attr("class", "bar")
                    .attr("x", 0)
                    .attr("y", d => y(d[0]))
                    .attr("width", d => x(d3.max(d[1], d => d3.max(d[1], d => d3.max(d[1], d => d.value)))))
                    .attr("height", y.bandwidth())
                    .attr("fill", d => sentimentColors[d[2]]);
            }});
        </script>
    </body>
    </html>
    """

    # Save the HTML template to a file
    with open("d3_visualization.html", "w") as html_file:
        html_file.write(html_template)
    
    # Display the HTML file in an iframe
    st.components.v1.iframe(src="d3_visualization.html", width=1000, height=800)
