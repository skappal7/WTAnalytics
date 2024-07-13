import streamlit as st
import pandas as pd
import json
import os

# Function to convert CSV data to hierarchical JSON
def csv_to_json(data):
    tree = {"name": "All Reviews", "children": []}
    
    data.columns = data.columns.str.strip()
    
    labels = data["Label"].unique()
    
    for label in labels:
        label_node = {"name": label, "children": []}
        label_data = data[data["Label"] == label]
        categories = label_data["Category"].unique()
        
        for category in categories:
            category_node = {"name": category, "children": []}
            category_data = label_data[label_data["Category"] == category]
            
            for _, row in category_data.iterrows():
                sentiment_type = row.get("sentiment_type", "").strip()
                if sentiment_type not in ["Negative", "Positive", "Neutral"]:
                    sentiment_type = "Neutral"
                
                sentiment_color = {
                    "Negative": "lightcoral",
                    "Positive": "lightgreen",
                    "Neutral": "lightgrey"
                }[sentiment_type]
                
                review_node = {
                    "name": row["Review"],
                    "color": sentiment_color
                }
                
                category_node["children"].append(review_node)
            
            label_node["children"].append(category_node)
        
        tree["children"].append(label_node)
    
    return tree

# Function to generate the HTML template
def generate_html(json_data):
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Text Analytics Visualization</title>
        <script src="https://d3js.org/d3.v6.min.js"></script>
        <style>
            body {{
                font-family: 'Poppins', sans-serif;
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
            .bar {{
                fill: steelblue;
            }}
            .bar:hover {{
                fill: orange;
            }}
            .axis-label {{
                font: 12px sans-serif;
            }}
        </style>
    </head>
    <body>
        <div id="dendrogram"></div>
        <div id="barchart"></div>
        <script>
            const data = {json.dumps(json_data)};
            
            const margin = {{top: 20, right: 90, bottom: 30, left: 90}},
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
                .on('click', function(event, d) {{
                    d.children = d.children ? null : d._children;
                    drawVisualization(data);
                }});

            node.append('circle')
                .attr('r', 5)
                .style('fill', d => d.data.color);

            node.append('text')
                .attr('dy', '.35em')
                .attr('x', d => d.children ? -13 : 13)
                .style('text-anchor', d => d.children ? 'end' : 'start')
                .text(d => d.data.name);

            // Grouped Horizontal Bar Chart
            const sentimentColors = {{
                'Negative': 'lightcoral',
                'Positive': 'lightgreen',
                'Neutral': 'lightgrey'
            }};

            const groupedData = data.children.map(group => ({
                label: group.name,
                categories: group.children.map(category => ({
                    category: category.name,
                    counts: category.children.reduce((acc, review) => {{
                        acc[review.color] = (acc[review.color] || 0) + 1;
                        return acc;
                    }}, {{}))
                }))
            }));

            const barMargin = {{top: 20, right: 30, bottom: 40, left: 90}};
            const barWidth = 960 - barMargin.left - barMargin.right;
            const barHeight = 500 - barMargin.top - barMargin.bottom;

            const svgBarChart = d3.select("#barchart").append("svg")
                .attr("width", barWidth + barMargin.left + barMargin.right)
                .attr("height", barHeight + barMargin.top + barMargin.bottom)
                .append("g")
                .attr("transform", "translate(" + barMargin.left + "," + barMargin.top + ")");

            const x = d3.scaleLinear()
                .range([0, barWidth])
                .domain([0, d3.max(groupedData, d => d3.max(d.categories, c => d3.max(Object.values(c.counts))))]);

            const y = d3.scaleBand()
                .range([barHeight, 0])
                .padding(0.1)
                .domain(groupedData.flatMap(d => d.categories.map(c => `${d.label} - ${c.category}`)));

            svgBarChart.append("g")
                .call(d3.axisLeft(y).tickSize(0))
                .selectAll("text")
                .attr("class", "axis-label");

            groupedData.forEach(group => {{
                const label = group.label;
                const categories = group.categories;

                categories.forEach(category => {{
                    const categoryName = category.category;
                    const counts = category.counts;

                    Object.keys(counts).forEach(color => {{
                        svgBarChart.append("rect")
                            .attr("class", `bar bar-{label}-{categoryName}`)
                            .attr("x", 0)
                            .attr("y", y(`${label} - ${categoryName}`))
                            .attr("width", x(counts[color]))
                            .attr("height", y.bandwidth())
                            .attr("fill", color);
                    }});
                }});
            }});
        </script>
    </body>
    </html>
    """
    return html_template

# Set up the Streamlit app structure
st.title("Generate Text Analytics Visualization")

# File upload component
uploaded_file = st.file_uploader("Upload your sentiment CSV file", type="csv")

if uploaded_file:
    try:
        # Read the CSV file
        data = pd.read_csv(uploaded_file)
        
        # Convert the data to hierarchical JSON format
        json_data = csv_to_json(data)
        
        if json_data:
            # Generate the HTML content
            html_content = generate_html(json_data)
            
            # Save the HTML content to a file
            output_file = "TextAnalytics.html"
            with open(output_file, "w") as file:
                file.write(html_content)
            
            st.success(f"HTML file has been created successfully: {output_file}")
            
            # Provide a download link for the HTML file
            st.markdown(f"[Download the HTML file](./{output_file})")
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
