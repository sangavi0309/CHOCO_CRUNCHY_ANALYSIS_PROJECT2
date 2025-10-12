import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

# ----------------- Streamlit Page Setup -----------------
st.set_page_config(page_title="ChocoCrunch Analytics 🍫", layout="wide")
st.title("🍫 ChocoCrunch Analytics: Sweet Stats & Sour Truths")
st.write("""
Explore the *ChocoCrunch* database!  
You can run SQL queries on the tables: **product_info**, **nutrient_info**, and **derived_metrics**.
""")

# ----------------- Connect / Create Database -----------------
conn = sqlite3.connect("chocolates.db")

# ----------------- Predefined Queries -----------------
queries = {
    "product_info": {
        "count_products_per_brand": {
            "question": "How many products are there per brand?",
            "sql": "SELECT brand, COUNT(*) AS product_count FROM product_info GROUP BY brand;"
        },
        "count_unique_products_per_brand": {
            "question": "How many unique products does each brand have?",
            "sql": "SELECT brand, COUNT(DISTINCT product_name) AS unique_products FROM product_info GROUP BY brand;"
        },
        "top5_brands_by_product_count": {
            "question": "Which are the top 5 brands by product count?",
            "sql": "SELECT brand, COUNT(*) AS product_count FROM product_info GROUP BY brand ORDER BY product_count DESC LIMIT 5;"
        },
        "products_missing_name": {
            "question": "Which products have missing product names?",
            "sql": "SELECT * FROM product_info WHERE product_name IS NULL OR product_name = '';"
        },
        "unique_brand_count": {
            "question": "How many unique brands are there?",
            "sql": "SELECT COUNT(DISTINCT brand) AS unique_brands FROM product_info;"
        },
        "products_code_starting_3": {
            "question": "Which products have a code starting with '3'?",
            "sql": "SELECT * FROM product_info WHERE product_code LIKE '3%';"
        }
    },

    "nutrient_info": {
        "top10_highest_energy": {
            "question": "What are the top 10 products with the highest energy (kcal)?",
            "sql": "SELECT product_name, energy_kcal_value FROM nutrient_info ORDER BY energy_kcal_value DESC LIMIT 10;"
        },
        "avg_sugars_per_nova": {
            "question": "What is the average sugar content per nova-group?",
            "sql": "SELECT nova_group, AVG(sugars_value) AS avg_sugars FROM nutrient_info GROUP BY nova_group;"
        },
        "count_fat_gt20": {
            "question": "How many products have fat content greater than 20g?",
            "sql": "SELECT COUNT(*) AS high_fat_products FROM nutrient_info WHERE fat_value > 20;"
        },
        "avg_carbs_per_product": {
            "question": "What is the average carbohydrate content per product?",
            "sql": "SELECT AVG(carbohydrates_value) AS avg_carbs FROM nutrient_info;"
        },
        "products_sodium_gt1g": {
            "question": "Which products have sodium content greater than 1g?",
            "sql": "SELECT product_name, sodium_value FROM nutrient_info WHERE sodium_value > 1;"
        },
        "count_nonzero_fvn": {
            "question": "How many products have non-zero fruits/vegetables/nuts content?",
            "sql": "SELECT COUNT(*) AS nonzero_fvn FROM nutrient_info WHERE fruits_vegetables_nuts_value > 0;"
        },
        "products_energy_gt500": {
            "question": "Which products have energy greater than 500 kcal?",
            "sql": "SELECT product_name, energy_kcal_value FROM nutrient_info WHERE energy_kcal_value > 500;"
        }
    },
        

    "derived_metrics": {
        "count_per_calorie_category": {
            "question": "How many products are there per calorie category?",
            "sql": "SELECT calorie_category, COUNT(*) AS product_count FROM derived_metrics GROUP BY calorie_category;"
        },
        "count_high_sugar": {
            "question": "How many products are marked as High Sugar?",
            "sql": "SELECT COUNT(*) AS high_sugar_count FROM derived_metrics WHERE sugar_category = 'High Sugar';"
        },
        "avg_ratio_high_calorie": {
            "question": "What is the average sugar-to-carb ratio for High Calorie products?",
            "sql": "SELECT AVG(sugar_to_carb_ratio) AS avg_ratio FROM derived_metrics WHERE calorie_category = 'High Calorie';"
        },
        "high_calorie_and_high_sugar": {
            "question": "Which products are both High Calorie and High Sugar?",
            "sql": "SELECT * FROM derived_metrics WHERE calorie_category = 'High Calorie' AND sugar_category = 'High Sugar';"
        },
        "count_ultra_processed": {
            "question": "How many products are marked as ultra-processed?",
            "sql": "SELECT COUNT(*) AS ultra_processed_count FROM derived_metrics WHERE ultra_processed = 1;"
        },
        "products_ratio_gt07": {
            "question": "Which products have sugar-to-carb ratio greater than 0.7?",
            "sql": "SELECT * FROM derived_metrics WHERE sugar_to_carb_ratio > 0.7;"
        },
        "avg_ratio_per_calorie_category": {
            "question": "What is the average sugar-to-carb ratio per calorie category?",
            "sql": "SELECT calorie_category, AVG(sugar_to_carb_ratio) AS avg_ratio FROM derived_metrics GROUP BY calorie_category;"
        }
    },

    "join_queries": {
        "top5_brands_high_calorie": {
            "question": "Which are the top 5 brands with the most High Calorie products?",
            "sql": "SELECT p.brand, COUNT(*) AS high_calorie_count FROM product_info p JOIN derived_metrics d ON p.product_id = d.product_id WHERE d.calorie_category = 'High Calorie' GROUP BY p.brand ORDER BY high_calorie_count DESC LIMIT 5;"
        },
        "avg_energy_per_calorie_category": {
            "question": "What is the average energy (kcal) for each calorie category?",
            "sql": "SELECT d.calorie_category, AVG(n.energy_kcal_value) AS avg_energy FROM derived_metrics d JOIN nutrient_info n ON d.product_id = n.product_id GROUP BY d.calorie_category;"
        },
        "ultra_processed_per_brand": {
            "question": "How many ultra-processed products are there per brand?",
            "sql": "SELECT p.brand, COUNT(*) AS ultra_processed_count FROM product_info p JOIN derived_metrics d ON p.product_id = d.product_id WHERE d.ultra_processed = 1 GROUP BY p.brand;"
        },
        "high_sugar_high_calorie_with_brand": {
            "question": "Which products are both High Sugar and High Calorie, along with their brand?",
            "sql": "SELECT p.brand, p.product_name FROM product_info p JOIN derived_metrics d ON p.product_id = d.product_id WHERE d.calorie_category = 'High Calorie' AND d.sugar_category = 'High Sugar';"
        },
        "avg_sugar_ultra_processed_per_brand": {
            "question": "What is the average sugar content per brand for ultra-processed products?",
            "sql": "SELECT p.brand, AVG(n.sugars_value) AS avg_sugar FROM product_info p JOIN nutrient_info n ON p.product_id = n.product_id JOIN derived_metrics d ON p.product_id = d.product_id WHERE d.ultra_processed = 1 GROUP BY p.brand;"
        },
        "fvn_per_calorie_category": {
            "question": "How many products with fruits/vegetables/nuts content exist in each calorie category?",
            "sql": "SELECT d.calorie_category, COUNT(*) AS count_with_fvn FROM derived_metrics d JOIN nutrient_info n ON d.product_id = n.product_id WHERE n.fruits_vegetables_nuts_value > 0 GROUP BY d.calorie_category;"
        },
        "top5_products_by_ratio": {
            "question": "Which are the top 5 products by sugar-to-carb ratio, with their calorie and sugar category?",
            "sql": "SELECT p.product_name, d.sugar_to_carb_ratio, d.calorie_category, d.sugar_category FROM product_info p JOIN derived_metrics d ON p.product_id = d.product_id ORDER BY d.sugar_to_carb_ratio DESC LIMIT 5;"
        }
    }
}

# ----------------- Tabs Layout -----------------
tab1, tab2, tab3, tab4 = st.tabs(["🔎 Queries", "📋 Tables", "📈 EDA Insights", "🔗 Compare Tables"])

# ----------------- Queries Tab -----------------
with tab1:
    st.subheader("Run a Query")
    query_type = st.selectbox("Choose a query category:", list(queries.keys()))
    query_choice = st.selectbox(
        "Choose a predefined query:",
        list(queries[query_type].keys()),
        format_func=lambda x: queries[query_type][x]["question"]
    )
    query = queries[query_type][query_choice]

    st.markdown(f"**❓ Question:** {query['question']}")
    st.code(query["sql"], language="sql")

    if st.button("▶️ Execute Query"):
        try:
            query_df = pd.read_sql_query(query["sql"], conn)

            if query_df.empty:
                st.warning("✅ Query executed successfully, but returned no rows.")
            else:
                st.success("✅ Query executed successfully!")
                st.dataframe(query_df, use_container_width=True)

                # Simple visualization logic
                if query_df.shape[1] >= 2:
                    col1, col2 = query_df.columns[:2]
                    chart = alt.Chart(query_df).mark_bar().encode(
                        x=alt.X(col1, sort='-y'),
                        y=col2,
                        tooltip=list(query_df.columns)
                    )
                    st.altair_chart(chart, use_container_width=True)

                # Download option
                csv = query_df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download Results as CSV", data=csv,
                                   file_name=f"{query_choice}.csv", mime="text/csv")
        except Exception as e:
            st.error(f"❌ Error executing query:\n\n{e}")
# ----------------- Tables Tab -----------------
with tab2:
    st.subheader("📋 Explore Raw Tables")

    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
    table_names = tables["name"].tolist()

    selected_table = st.selectbox("Choose a table to view:", table_names, key="raw_table")

    if selected_table:
        df = pd.read_sql_query(f"SELECT * FROM {selected_table} LIMIT 100;", conn)
        st.markdown(f"**Showing first 100 rows of `{selected_table}`**")
        st.dataframe(df, use_container_width=True)

        # Download full table
        full_df = pd.read_sql_query(f"SELECT * FROM {selected_table};", conn)
        csv = full_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            f"⬇️ Download {selected_table} as CSV",
            data=csv,
            file_name=f"{selected_table}.csv",
            mime="text/csv"
        )

# ----------------- EDA Insights Tab -----------------
import plotly.express as px
import numpy as np

# ----------------- Styling & Helpers -----------------
PALETTE = px.colors.qualitative.Vivid  # Alt options: Bold, D3, Set3
BG_COLOR = "#0f1116"  # for dark vibes; switch to white for light
PRIMARY = "#7c3aed"   # purple accent
ACCENT = "#22d3ee"    # cyan accent

def kpi_metric(label, value, help_text=None):
    st.metric(label, value)
    if help_text:
        st.caption(help_text)

def numeric_columns(df):
    return df.select_dtypes(include="number").columns.tolist()

def categorical_columns(df):
    return df.select_dtypes(include=["object", "category"]).columns.tolist()

def nice_number(n):
    return f"{n:,.0f}" if isinstance(n, (int, np.integer)) else f"{n:,.2f}"

def show_missingness(df):
    nulls = df.isnull().sum().sort_values(ascending=False)
    nulls = nulls[nulls > 0]
    if nulls.empty:
        st.success("No missing values detected.")
        return
    miss_df = nulls.reset_index()
    miss_df.columns = ["column", "missing_count"]
    miss_df["missing_pct"] = (miss_df["missing_count"] / len(df)) * 100
    st.markdown("**Missingness by column**")
    fig = px.bar(
        miss_df,
        x="column", y="missing_pct",
        color="missing_pct",
        color_continuous_scale="Turbo",
        labels={"missing_pct": "Missing (%)"},
        height=350
    )
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def show_correlation(df, title="Correlation heatmap"):
    num_cols = numeric_columns(df)
    if len(num_cols) < 2:
        st.info("Not enough numeric columns for correlation.")
        return
    corr = df[num_cols].corr()
    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu",
        aspect="auto",
        title=title
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

def dist_grid(df, num_cols, bins=30, max_cols=6):
    if not num_cols:
        st.info("No numeric columns found.")
        return
    cols = num_cols[:max_cols]
    st.markdown("**Distributions**")
    for col in cols:
        fig = px.histogram(
            df, x=col, nbins=bins,
            marginal="rug",
            color_discrete_sequence=[PRIMARY],
            title=f"Distribution of {col}"
        )
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)

def categorical_bar(df, cat_col, top_n=20, metric_col=None, agg="count"):
    if agg == "count" or metric_col is None:
        g = df.groupby(cat_col).size().reset_index(name="count").sort_values("count", ascending=False).head(top_n)
        fig = px.bar(
            g, x=cat_col, y="count",
            color=cat_col, color_discrete_sequence=PALETTE,
            title=f"Top {top_n} {cat_col} by count"
        )
    else:
        g = df.groupby(cat_col)[metric_col].mean().reset_index().sort_values(metric_col, ascending=False).head(top_n)
        fig = px.bar(
            g, x=cat_col, y=metric_col,
            color=cat_col, color_discrete_sequence=PALETTE,
            title=f"Top {top_n} {cat_col} by avg {metric_col}"
        )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

def scatter_auto(df, x_col, y_col, color_col=None):
    fig = px.scatter(
        df, x=x_col, y=y_col, color=color_col,
        trendline="ols",
        color_discrete_sequence=PALETTE,
        title=f"{y_col} vs {x_col}"
    )
    fig.update_traces(marker=dict(size=9, opacity=0.85))
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

def box_violin(df, num_col, cat_col=None):
    c1, c2 = st.columns(2)
    with c1:
        fig_box = px.box(df, x=cat_col, y=num_col, color=cat_col if cat_col else None,
                         points="suspectedoutliers", color_discrete_sequence=PALETTE,
                         title=f"Box plot of {num_col}" + (f" by {cat_col}" if cat_col else ""))
        fig_box.update_layout(showlegend=False, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_box, use_container_width=True)
    with c2:
        fig_violin = px.violin(df, x=cat_col, y=num_col, color=cat_col if cat_col else None,
                               box=True, points="suspectedoutliers",
                               color_discrete_sequence=PALETTE,
                               title=f"Violin plot of {num_col}" + (f" by {cat_col}" if cat_col else ""))
        fig_violin.update_layout(showlegend=False, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_violin, use_container_width=True)

# ----------------- Beautiful EDA Tab -----------------
with tab3:
    st.subheader("📈 EDA insights")

    selected_table = st.selectbox("Choose a table for EDA:", table_names, key="eda_table_v2")

    if selected_table:
        df = pd.read_sql_query(f"SELECT * FROM {selected_table};", conn)
        num_cols = numeric_columns(df)
        cat_cols = categorical_columns(df)

        # KPIs
        st.markdown("**Quick KPIs**")
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi_metric("Rows", nice_number(len(df)))
        with k2:
            kpi_metric("Columns", nice_number(df.shape[1]))
        with k3:
            kpi_metric("Numeric cols", nice_number(len(num_cols)))
        with k4:
            kpi_metric("Categorical cols", nice_number(len(cat_cols)))

        st.divider()

        # Missingness & correlation
        c_top = st.tabs(["Missingness", "Correlation", "Distributions", "Category analysis", "Custom explore"])
        with c_top[0]:
            show_missingness(df)
        with c_top[1]:
            show_correlation(df)

        # Distributions
        with c_top[2]:
            bins = st.slider("Bins for histograms", 10, 80, 30, 2)
            dist_grid(df, num_cols, bins=bins)

        # Category analysis
        with c_top[3]:
            if cat_cols:
                cat_col = st.selectbox("Categorical column", cat_cols, key="eda_cat_col")
                mode = st.radio("Aggregation mode", ["count", "average of a numeric column"], horizontal=True)
                if mode == "count":
                    top_n = st.slider("Top N", 5, 50, 20, 5)
                    categorical_bar(df, cat_col, top_n=top_n, metric_col=None, agg="count")
                else:
                    metric_col = st.selectbox("Numeric column to average", num_cols, key="eda_metric_col")
                    top_n = st.slider("Top N", 5, 50, 20, 5)
                    categorical_bar(df, cat_col, top_n=top_n, metric_col=metric_col, agg="avg")
            else:
                st.info("No categorical columns found.")

        # Custom explore
        with c_top[4]:
            if len(num_cols) >= 2:
                c1, c2 = st.columns(2)
                with c1:
                    x_col = st.selectbox("X axis (numeric)", num_cols, key="eda_x")
                with c2:
                    y_col = st.selectbox("Y axis (numeric)", [c for c in num_cols if c != st.session_state.get("eda_x")], key="eda_y")
                color_col = st.selectbox("Color (optional categorical)", [None] + cat_cols, key="eda_color")
                scatter_auto(df, x_col, y_col, color_col if color_col != None else None)
                # Box/violin for outliers & distribution shape
                num_for_box = st.selectbox("Numeric column for box/violin", num_cols, key="eda_box_num")
                cat_for_box = st.selectbox("Category (optional)", [None] + cat_cols, key="eda_box_cat")
                box_violin(df, num_for_box, cat_for_box if cat_for_box != None else None)
            else:
                st.info("Not enough numeric columns for custom scatter/box.")


# ----------------- Compare Tables Tab -----------------
with tab4:
    st.subheader("🔗 Compare Tables")

    # Select two tables to join
    table1 = st.selectbox("Choose first table:", table_names, key="compare1")
    table2 = st.selectbox("Choose second table:", table_names, key="compare2")

    # Assume common key is product_id
    join_key = st.text_input("Enter join key (default: product_code)", "product_code")

    if st.button("🔍 Compare"):
        try:
            df1 = pd.read_sql_query(f"SELECT * FROM {table1};", conn)
            df2 = pd.read_sql_query(f"SELECT * FROM {table2};", conn)

            if join_key in df1.columns and join_key in df2.columns:
                merged = pd.merge(df1, df2, on=join_key, how="inner")

                st.success(f"✅ Joined {table1} and {table2} on `{join_key}`")
                st.dataframe(merged.head(100), use_container_width=True)
            else:
                st.error(f"❌ Join key `{join_key}` not found in both tables.")

        except Exception as e:
            st.error(f"❌ Error comparing tables:\n\n{e}")
# ----------------- Summary & Insights Tab -----------------
with st.expander("📊 Summary Insights & Recommendations"):
    st.markdown("""
    ### 🧾 Key Project Summary
    The *ChocoCrunch Analytics* project provides a complete end-to-end
    nutrition analysis pipeline — from data extraction to visualization.
    Data was collected from the *OpenFoodFacts API*, cleaned, and organized
    into three SQL tables: product_info, nutrient_info, and derived_metrics.
    Each table was explored through *27 structured SQL queries* and visualized
    using *Streamlit* dashboards for interactive exploration.

    ### 🍫 Major Findings
    - *High-Calorie Products:* Several chocolate brands contain products exceeding
      *500 kcal per 100 g, placing them in the *High Calorie category.
    - *Sugar-Heavy Items:* Many products show a *sugar_to_carb_ratio > 0.7*,
      meaning more than 70 % of carbohydrates come from sugars.
    - *Ultra-Processed Dominance:* Over half the products belong to *NOVA Group 4*,
      indicating they are ultra-processed chocolates.
    - *Brand Trends:* A few global brands contribute most to both
      High Calorie and High Sugar categories, while smaller artisanal
      brands tend to score lower on calories and sugar.
    - *Nutrient Relationships:* Calories and sugar levels show a strong
      positive correlation, confirming that sweeter chocolates are generally
      more energy-dense.

    ### 💡 Health & Business Recommendations
    - Encourage production and promotion of *lower-sugar alternatives*
      (sugar < 20 g/100 g, calories < 500 kcal/100 g).
    - Highlight *brands with balanced sugar-to-carb ratios (< 0.4)* as
      healthier choices.
    - For consumers, prefer chocolates labeled Low Calorie and
      Moderate Sugar in the derived metrics.
    - For businesses, these insights help identify *market gaps* for
      healthier chocolate options and data-driven product reformulation.

    ---
    *This dashboard demonstrates how data-driven analytics can guide healthier
    consumer choices and strategic product development in the chocolate market.*
    """)


