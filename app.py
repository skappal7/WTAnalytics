import pandas as pd
import plotly.express as px
import streamlit as st

# Streamlit app
st.title("Interactive Sentiment Tree Map")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Color pickers in the sidebar
st.sidebar.header("Choose Sentiment Colors")
positive_color = st.sidebar.color_picker("Positive Sentiment Color", "#90EE90")  # lightgreen
negative_color = st.sidebar.color_picker("Negative Sentiment Color", "#F08080")  # lightcoral
neutral_color = st.sidebar.color_picker("Neutral Sentiment Color", "#D3D3D3")    # lightgray

if uploaded_file is not None:
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file)
    
    # Display the dataframe to verify data is loaded correctly
    st.write("Data Preview:")
    st.write(df.head())

    # Verify column names
    st.write("Column names in the data:")
    st.write(df.columns.tolist())

    # Check for unique values in the required columns
    st.write("Unique values in 'Label' column:")
    st.write(df['Label'].unique())
    
    st.write("Unique values in 'Category' column:")
    st.write(df['Category'].unique())
    
    st.write("Unique values in 'sentiment_type' column:")
    st.write(df['sentiment_type'].unique())

    # Preprocess data
    # Drop rows with missing values in hierarchy columns
    df.dropna(subset=['Label', 'Category', 'sentiment_type'], inplace=True)

    # Aggregate data to count occurrences
    aggregated_df = df.groupby(['Label', 'Category', 'sentiment_type']).size().reset_index(name='counts')

    # Create hierarchical data structure for tree map
    try:
        fig = px.treemap(
            aggregated_df,
            path=['Label', 'Category', 'sentiment_type'],
            values='counts',  # Use counts as the size of each block
            color='sentiment_type',
            color_discrete_map={
                'Positive': positive_color,
                'Negative': negative_color,
                'Neutral': neutral_color
            },
            hover_data={'counts': True}
        )

        fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

        st.plotly_chart(fig, use_container_width=True)
    except ValueError as e:
        st.error(f"ValueError: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.write("Please upload a CSV file to generate the tree map.")
