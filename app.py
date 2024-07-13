import streamlit as st
import pandas as pd
import json
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import base64

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Set page configuration
st.set_page_config(layout="wide", page_title="Review Analysis Visualization")

# Title of the app
st.title("Review Analysis Visualization")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)
    
    # Data processing
    def process_data(df, sentiment_filter='All'):
        hierarchy = {"name": "All Reviews", "children": []}
        labels = defaultdict(lambda: {"name": "", "children": []})
        
        stop_words = set(stopwords.words('english'))
        
        for _, row in df.iterrows():
            if sentiment_filter != 'All' and row['sentiment_type'].lower() != sentiment_filter.lower():
                continue
            
            label = row['Label']
            category = row['Category']
            review = row['Review']
            sentiment = row['sentiment']
            sentiment_type = row['sentiment_type']
            
            if label not in labels:
                labels[label] = {"name": label, "children": []}
                hierarchy["children"].append(labels[label])
            
            category_node = next((c for c in labels[label]["children"] if c["name"] == category), None)
            if not category_node:
                category_node = {"name": category, "children": [], "reviews": []}
                labels[label]["children"].append(category_node)
            
            category_node["reviews"].append({
                "text": review,
                "sentiment": sentiment,
                "sentiment_type": sentiment_type
            })
            
            # Process words for word cloud
            words = word_tokenize(review.lower())
            words = [word for word in words if word.isalnum() and word not in stop_words]
            for word in words:
                if "words" not in category_node:
                    category_node["words"] = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0})
                category_node["words"][word][sentiment_type] += 1
        
        return hierarchy

    # Process the data
    processed_data = process_data(df)

    # Convert to JSON for D3.js
    json_data = json.dumps(processed_data)

    # Calculate summary statistics
    total_reviews = len(df)
    overall_sentiment = df['sentiment'].mean()
    positive_count = len(df[df['sentiment_type'] == 'positive'])
    negative_count = len(df[df['sentiment_type'] == 'negative'])
    neutral_count = len(df[df['sentiment_type'] == 'neutral'])

    # Display summary statistics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Reviews", total_reviews)
    col2.metric("Overall Sentiment", f"{overall_sentiment:.2f}")
    col3.metric("Positive Reviews", positive_count)
    col4.metric("Negative Reviews", negative_count)
    col5.metric("Neutral Reviews", neutral_count)

    # Sentiment filter
    sentiment_filter = st.radio(
        "Filter by sentiment",
        ('All', 'Positive', 'Negative', 'Neutral')
    )

    # Update data based on sentiment filter
    filtered_data = process_data(df, sentiment_filter)
    json_data = json.dumps(filtered_data)

    # Placeholder for D3.js visualization
    st.markdown("## Dendrogram and Bar Chart")
    viz_placeholder = st.empty()

    # D3.js code (as a string)
    d3_code = """
    <style>
    .node circle {
      fill: #fff;
      stroke: steelblue;
      stroke-width: 3px;
    }
    .node text { font: 12px sans-serif; }
    .link { fill: none; stroke: #ccc; stroke-width: 2px; }
    .tooltip { position: absolute; text-align: center; padding: 2px; font: 12px sans-serif; background: lightsteelblue; border: 0px; border-radius: 8px; pointer-events: none; }
    </style>
    <div id="visualization"></div>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script>
    // D3.js code
    const data = JSON.parse('""" + json_data + """');
    
    const width = 1000;
    const height = 800;
    const margin = {top: 20, right: 90, bottom: 30, left: 90};
    
    const svg = d3.select("#visualization")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
    
    const treemap = d3.tree().size([height, width - 160]);
    
    const root = d3.hierarchy(data);
    root.x0 = height / 2;
    root.y0 = 0;
    
    update(root);
    
    function update(source) {
        const treeData = treemap(root);
        const nodes = treeData.descendants();
        const links = treeData.descendants().slice(1);
    
        nodes.forEach(d => { d.y = d.depth * 180 });
    
        const node = svg.selectAll('g.node')
            .data(nodes, d => d.id || (d.id = ++i));
    
        const nodeEnter = node.enter().append('g')
            .attr('class', 'node')
            .attr("transform", d => `translate(${source.y0},${source.x0})`)
            .on('click', click);
    
        nodeEnter.append('circle')
            .attr('r', 1e-6)
            .style("fill", d => d._children ? "lightsteelblue" : "#fff");
    
        nodeEnter.append('text')
            .attr("dy", ".35em")
            .attr("x", d => d.children || d._children ? -13 : 13)
            .attr("text-anchor", d => d.children || d._children ? "end" : "start")
            .text(d => d.data.name);
    
        const nodeUpdate = nodeEnter.merge(node);
    
        nodeUpdate.transition()
            .duration(750)
            .attr("transform", d => `translate(${d.y},${d.x})`);
    
        nodeUpdate.select('circle')
            .attr('r', 10)
            .style("fill", d => d._children ? "lightsteelblue" : "#fff");
    
        const nodeExit = node.exit().transition()
            .duration(750)
            .attr("transform", d => `translate(${source.y},${source.x})`)
            .remove();
    
        nodeExit.select('circle')
            .attr('r', 1e-6);
    
        nodeExit.select('text')
            .style('fill-opacity', 1e-6);
    
        const link = svg.selectAll('path.link')
            .data(links, d => d.id);
    
        const linkEnter = link.enter().insert('path', "g")
            .attr("class", "link")
            .attr('d', d => {
                const o = {x: source.x0, y: source.y0};
                return diagonal(o, o);
            });
    
        const linkUpdate = linkEnter.merge(link);
    
        linkUpdate.transition()
            .duration(750)
            .attr('d', d => diagonal(d, d.parent));
    
        link.exit().transition()
            .duration(750)
            .attr('d', d => {
                const o = {x: source.x, y: source.y};
                return diagonal(o, o);
            })
            .remove();
    
        nodes.forEach(d => {
            d.x0 = d.x;
            d.y0 = d.y;
        });
    }
    
    function diagonal(s, d) {
        return `M ${s.y} ${s.x}
                C ${(s.y + d.y) / 2} ${s.x},
                  ${(s.y + d.y) / 2} ${d.x},
                  ${d.y} ${d.x}`;
    }
    
    function click(event, d) {
        if (d.children) {
            d._children = d.children;
            d.children = null;
        } else {
            d.children = d._children;
            d._children = null;
        }
        update(d);
    
        if (d.data.reviews) {
            showBarChart(d.data);
        }
    }
    
    function showBarChart(data) {
        d3.select("#barChart").remove();
    
        const margin = {top: 20, right: 20, bottom: 30, left: 40};
        const width = 300 - margin.left - margin.right;
        const height = 200 - margin.top - margin.bottom;
    
        const x = d3.scaleBand()
            .range([0, width])
            .padding(0.1);
        const y = d3.scaleLinear()
            .range([height, 0]);
    
        const barSvg = svg.append("g")
            .attr("id", "barChart")
            .attr("transform", `translate(${width + 100},${height / 2})`);
    
        const sentimentCounts = {
            positive: data.reviews.filter(r => r.sentiment_type === 'positive').length,
            negative: data.reviews.filter(r => r.sentiment_type === 'negative').length,
            neutral: data.reviews.filter(r => r.sentiment_type === 'neutral').length
        };
    
        const barData = Object.entries(sentimentCounts).map(([key, value]) => ({sentiment: key, count: value}));
    
        x.domain(barData.map(d => d.sentiment));
        y.domain([0, d3.max(barData, d => d.count)]);
    
        barSvg.selectAll(".bar")
            .data(barData)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", d => x(d.sentiment))
            .attr("width", x.bandwidth())
            .attr("y", d => y(d.count))
            .attr("height", d => height - y(d.count))
            .attr("fill", d => d.sentiment === 'positive' ? 'green' : d.sentiment === 'negative' ? 'red' : 'gray');
    
        barSvg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(x));
    
        barSvg.append("g")
            .call(d3.axisLeft(y));
    
        // Word cloud
        const words = data.words;
        const wordData = Object.entries(words).map(([word, counts]) => ({
            text: word,
            size: counts.positive + counts.negative + counts.neutral
        })).sort((a, b) => b.size - a.size).slice(0, 20);
    
        const wordCloudWidth = 300;
        const wordCloudHeight = 200;
    
        const wordCloudSvg = svg.append("g")
            .attr("id", "wordCloud")
            .attr("transform", `translate(${width + 450},${height / 2})`);
    
        const wordScale = d3.scaleLinear()
            .domain([0, d3.max(wordData, d => d.size)])
            .range([10, 50]);
    
        wordCloudSvg.selectAll("text")
            .data(wordData)
            .enter().append("text")
            .style("font-size", d => `${wordScale(d.size)}px`)
            .style("fill", "steelblue")
            .attr("text-anchor", "middle")
            .attr("transform", (d, i) => `translate(${(i % 5) * 60},${Math.floor(i / 5) * 40})`)
            .text(d => d.text);
    }
    
    // Zoom functionality
    const zoom = d3.zoom()
        .scaleExtent([0.5, 3])
        .on("zoom", zoomed);
    
    svg.call(zoom);
    
    function zoomed(event) {
        svg.attr("transform", event.transform);
    }
    
    </script>
    """

    # Inject D3.js code
    viz_placeholder.markdown(d3_code, unsafe_allow_html=True)

else:
    st.write("Please upload a CSV file to begin.")
