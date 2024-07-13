import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

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
    
    # Convert the data to JSON format
    json_data = data.to_json(orient='records')

    # Debug: Display JSON data
    st.write("JSON Data")
    st.json(json_data)

    # HTML template to embed the D3.js visualization
    html_template = f"""
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
            const data = {json_data};
            
            // Create a map of unique IDs to ensure a single root
            const idMap = new Map();
            data.forEach(d => idMap.set(d.category, d));

            const rootId = Array.from(idMap.keys())[0];
            
            // Process the data for the dendrogram
            const root = d3.stratify()
                .id(function(d) {{ return d.category; }})
                .parentId(function(d) {{ return d.label; }})(data)
                .sum(function(d) {{ return d.value; }})
                .sort(function(a, b) {{ return b.height - a.height || b.value - a.value; }});

            // Ensure single root
            if (root.children.length > 1) {{
                console.error("Multiple roots detected");
                document.getElementById("dendrogram").innerHTML = "<p>Multiple roots detected. Please check the data structure.</p>";
            }} else {{
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
                        .x(function(d) {{ return d.y; }})
                        .y(function(d) {{ return d.x; }}));

                const node = svgDendrogram.selectAll(".dendrogram-node")
                    .data(root.descendants())
                    .enter().append("g")
                    .attr("class", "dendrogram-node")
                    .attr("transform", function(d) {{ return "translate(" + d.y + "," + d.x + ")"; }});

                node.append("circle")
                    .attr("r", 2.5);

                node.append("text")
                    .attr("dy", 3)
                    .attr("x", function(d) {{ return d.children ? -8 : 8; }})
                    .style("text-anchor", function(d) {{ return d.children ? "end" : "start"; }})
                    .text(function(d) {{ return d.data.name; }});

                // Process the data for the bar chart
                const sentimentColors = {{
                    'Negative': 'lightcoral',
                    'Positive': 'lightgreen',
                    'Neutral': 'lightgrey'
                }};

                const groupedData = d3.groups(data, function(d) {{ return d.label; }}, function(d) {{ return d.category; }}, function(d) {{ return d.sentiment; }});

                // Create the bar chart
                const margin = {{ top: 20, right: 30, bottom: 40, left: 90 }};
                const width = 960 - margin.left - margin.right;
                const height = 500 - margin.top - margin.bottom;

                const svgBarChart = d3.select("#barchart").append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

                const x = d3.scaleLinear()
                    .range([0, width])
                    .domain([0, d3.max(groupedData, function(d) {{ return d3.max(d[1], function(d) {{ return d3.max(d[1], function(d) {{ return d3.max(d[1], function(d) {{ return d.value; }}); }}); }}); }})]);

                const y = d3.scaleBand()
                    .range([height, 0])
                    .padding(0.1)
                    .domain(groupedData.map(function(d) {{ return d[0]; }}));

                svgBarChart.append("g")
                    .call(d3.axisLeft(y).tickSize(0))
                    .selectAll("text")
                    .attr("class", "axis-label");

                groupedData.forEach(function(group) {{
                    const label = group[0];
                    const categories = group[1];

                    const ySubgroup = d3.scaleBand()
                        .domain(categories.map(function(d) {{ return d[0]; }}))
                        .range([0, y.bandwidth()])
                        .padding(0.05);

                    categories.forEach(function(category) {{
                        const categoryName = category[0];
                        const sentiments = category[1];

                        svgBarChart.selectAll(".bar-" + label + "-" + categoryName)
                            .data(sentiments)
                            .enter().append("rect")
                            .attr("class", "bar bar-" + label + "-" + categoryName)
                            .attr("x", 0)
                            .attr("y", function(d) {{ return y(label) + ySubgroup(d[0]); }})
                            .attr("width", function(d) {{ return x(d.value); }})
                            .attr("height", ySubgroup.bandwidth())
                            .attr("fill", function(d) {{ return sentimentColors[d[0]]; }});
                    }});
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    # Display the HTML template using Streamlit components
    components.html(html_template, height=800)
