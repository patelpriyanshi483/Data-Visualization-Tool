import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Configure Streamlit page
st.set_page_config(page_title="Interactive Data Visualization Tool", layout="wide")
st.title("📊 Interactive Data Visualization Tool")

# Custom styling for upload button
st.markdown("""
    <style>
    section[data-testid="stFileUploader"] > label div.st-bx {
        background-color: #28a745;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if "plot_type" not in st.session_state:
    st.session_state.plot_type = None

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📋 Dataset Preview")
    st.dataframe(df.head())

    all_columns = df.columns.tolist()
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("🎛️ Select Plot Type")
        plot_buttons = [
            "Scatter Plot", "Line Plot", "Histogram", "Box Plot", "Heatmap",
            "Bar Plot", "Area Plot", "Pie Chart", "Donut Chart",
            "Violin Plot", "Count Plot", "Pair Plot"
        ]

        button_cols = st.columns(2)
        for idx, plot in enumerate(plot_buttons):
            with button_cols[idx % 2]:
                if st.button(plot):
                    st.session_state.plot_type = plot

        lib_choice = st.radio("Library", ["Plotly (Interactive)", "Matplotlib/Seaborn"])
        plot_type = st.session_state.plot_type

        # Axis selections
        if plot_type in ["Pie Chart", "Donut Chart"]:
            cat_col = st.selectbox("Category (Label)", categorical_columns)
            val_col = st.selectbox("Value", numeric_columns)
            x_col = y_col = None
        elif plot_type in ["Pair Plot", "Heatmap"]:
            x_col = y_col = cat_col = val_col = None
        else:
            x_col = st.selectbox("X-Axis", all_columns)
            y_col = None
            if plot_type not in ["Histogram", "Count Plot", "Bar Plot", "Area Plot"]:
                y_col = st.selectbox("Y-Axis", numeric_columns)

    with col2:
        plot_type = st.session_state.plot_type
        if plot_type:
            st.subheader(f"📊 {plot_type}")

            # Plotly Visualizations
            if lib_choice == "Plotly (Interactive)":
                if plot_type == "Scatter Plot":
                    fig = px.scatter(df, x=x_col, y=y_col, color=x_col)
                elif plot_type == "Line Plot":
                    fig = px.line(df, x=x_col, y=y_col)
                elif plot_type == "Histogram":
                    fig = px.histogram(df, x=x_col)
                elif plot_type == "Box Plot":
                    fig = px.box(df, x=x_col, y=y_col)
                elif plot_type == "Heatmap":
                    fig = px.imshow(df[numeric_columns].corr(), text_auto=True)
                elif plot_type == "Bar Plot":
                    fig = px.bar(df, x=x_col, y=y_col)
                elif plot_type == "Area Plot":
                    fig = px.area(df, x=x_col, y=y_col)
                elif plot_type == "Pie Chart":
                    fig = px.pie(df, names=cat_col, values=val_col)
                elif plot_type == "Donut Chart":
                    fig = px.pie(df, names=cat_col, values=val_col, hole=0.4)
                elif plot_type == "Violin Plot":
                    fig = px.violin(df, x=x_col, y=y_col, box=True, points="all")
                elif plot_type == "Count Plot":
                    fig = px.bar(df[x_col].value_counts().reset_index(), x='index', y=x_col)
                elif plot_type == "Pair Plot":
                    fig = px.scatter_matrix(df[numeric_columns])
                st.plotly_chart(fig, use_container_width=True)

            # Matplotlib/Seaborn Visualizations
            else:
                plt.figure(figsize=(10, 6))
                if plot_type == "Scatter Plot":
                    sns.scatterplot(data=df, x=x_col, y=y_col)
                elif plot_type == "Line Plot":
                    sns.lineplot(data=df, x=x_col, y=y_col)
                elif plot_type == "Histogram":
                    sns.histplot(data=df, x=x_col, bins=30, kde=True)
                elif plot_type == "Box Plot":
                    sns.boxplot(data=df, x=x_col, y=y_col)
                elif plot_type == "Heatmap":
                    sns.heatmap(df[numeric_columns].corr(), annot=True, cmap="coolwarm")
                elif plot_type == "Bar Plot":
                    sns.barplot(data=df, x=x_col, y=y_col)
                elif plot_type == "Area Plot":
                    df_sorted = df.sort_values(by=x_col)
                    plt.fill_between(df_sorted[x_col], df_sorted[y_col], alpha=0.5)
                elif plot_type in ["Pie Chart", "Donut Chart"]:
                    plt.pie(df[val_col], labels=df[cat_col], autopct='%1.1f%%',
                            startangle=90, wedgeprops={'width': 0.6 if plot_type == "Donut Chart" else 1})
                    plt.axis('equal')
                elif plot_type == "Violin Plot":
                    sns.violinplot(data=df, x=x_col, y=y_col)
                elif plot_type == "Count Plot":
                    sns.countplot(data=df, x=x_col)
                elif plot_type == "Pair Plot":
                    sns.pairplot(df[numeric_columns])
                st.pyplot(plt)

            # Overview AFTER plot
            st.subheader("📌 Overview")
            if plot_type in ["Scatter Plot", "Line Plot", "Box Plot", "Violin Plot", "Area Plot"] and y_col:
                mean = df[y_col].mean()
                min_ = df[y_col].min()
                max_ = df[y_col].max()
                trend = df[y_col].diff().mean()

                st.markdown(f"- **Average `{y_col}`**: `{mean:.2f}`")
                st.markdown(f"- **Min `{y_col}`**: `{min_:.2f}` | Max: `{max_:.2f}`")
                if trend > 0:
                    st.success(f"📈 `{y_col}` shows an increasing trend.")
                elif trend < 0:
                    st.error(f"📉 `{y_col}` shows a decreasing trend.")
                else:
                    st.warning(f"➖ `{y_col}` appears stable.")

            elif plot_type == "Histogram":
                st.markdown(f"- Most frequent value in `{x_col}`: `{df[x_col].value_counts().idxmax()}`")
            elif plot_type == "Heatmap":
                st.info("🧊 Heatmap reflects variable correlation.")
            elif plot_type in ["Pie Chart", "Donut Chart"]:
                top_cat = df[cat_col].value_counts().idxmax()
                st.markdown(f"- Top category in `{cat_col}`: `{top_cat}`")
            else:
                st.info("No specific insight available.")
