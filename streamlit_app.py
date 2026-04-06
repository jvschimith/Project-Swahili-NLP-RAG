"""
Streamlit Dashboard - Swahili News Analysis (ENHANCED)

Enhanced version with:
- Save analyzed URLs to database for future study
- Real linguistic insights (TTR, readability, morphology, n-grams)
- Better database analytics with actual analysis
- Improved visualizations

Run with:
    streamlit run streamlit_app.py
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from collections import Counter

# Configure page
st.set_page_config(
    page_title="Swahili News Analyzer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .positive {color: #4CAF50;}
    .negative {color: #f44336;}
    .neutral {color: #9E9E9E;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📰 Swahili News Analyzer</h1>', unsafe_allow_html=True)
st.markdown("**Analyze Swahili news articles in real-time with AI-powered insights**")

# Sidebar
st.sidebar.title("⚙️ Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["🔗 URL Analysis", "📊 Database Analytics", "📈 Sentiment Trends", "🔤 Linguistic Insights"]
)

st.sidebar.markdown("---")

# Live stats in sidebar
try:
    stats_response = requests.get(f"{API_URL}/stats", timeout=2)
    if stats_response.status_code == 200:
        stats = stats_response.json()
        st.sidebar.markdown("### 📊 Database Stats")
        st.sidebar.metric("Saved Articles", f"{stats['news_articles']:,}")
        st.sidebar.metric("Total Terms", f"{stats['terms']:,}")
        st.sidebar.caption("_Updates automatically_")
except:
    pass  # Silently fail if API not available

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Sample URLs")
st.sidebar.markdown("""
- [BBC Swahili](https://www.bbc.com/swahili)
- [VOA Swahili](https://www.voaswahili.com/)
- [DW Swahili](https://www.dw.com/sw)
- [Mwananchi](https://www.mwananchi.co.tz/)
""")

# ==================== PAGE 1: URL ANALYSIS ====================
if page == "🔗 URL Analysis":
    st.header("🔗 Analyze News from URL")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        url = st.text_input(
            "Enter News Article URL",
            placeholder="https://www.bbc.com/swahili/...",
            help="Paste a link to a Swahili news article"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    # Option to save to database
    save_to_db = st.checkbox("💾 Save this article to database for future analysis", value=True,
                             help="Store this article in your database to track trends over time")
    
    if analyze_button and url:
        with st.spinner("Fetching and analyzing article..."):
            try:
                # Call API
                response = requests.post(
                    f"{API_URL}/analyze/url",
                    json={"url": url},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        st.success("✅ Analysis Complete!")
                        
                        # Save to database if checked
                        if save_to_db:
                            with st.spinner("Saving to database..."):
                                try:
                                    # Get category from user
                                    category = st.selectbox(
                                        "Select article category:",
                                        ["Politics", "Economy", "Sports", "Culture", "Technology", "Health", "Education", "Other"],
                                        index=0,
                                        key="category_select"
                                    )
                                    
                                    save_response = requests.post(
                                        f"{API_URL}/news/save",
                                        json={
                                            "content": data.get('full_text', data['text_preview'])[:5000],  # Limit size
                                            "category": category,
                                            "source_url": url,
                                            "sentiment_polarity": data['sentiment']['polarity'],
                                            "sentiment_confidence": data['sentiment']['confidence'],
                                            "sentiment_label": data['sentiment']['label']
                                        }
                                    )
                                    if save_response.status_code in [200, 201]:
                                        save_data = save_response.json()
                                        
                                        # Get updated count
                                        stats_response = requests.get(f"{API_URL}/stats")
                                        if stats_response.status_code == 200:
                                            updated_count = stats_response.json()['news_articles']
                                            st.success(f"""
                                            ✅ **Article saved successfully!**
                                            
                                            - Article ID: {save_data.get('article_id', 'N/A')}
                                            - Category: {category}
                                            - Sentiment: {data['sentiment']['label'].title()}
                                            - **Total articles in database: {updated_count}**
                                            
                                            💡 Go to "📊 Database Analytics" tab to see all saved articles!
                                            """)
                                        else:
                                            st.success("💾 Article saved to database! Go to 'Database Analytics' to view it.")
                                    else:
                                        st.warning(f"⚠️ Save failed: {save_response.status_code}. Check API logs.")
                                except requests.exceptions.ConnectionError:
                                    st.error("❌ Cannot connect to API. Make sure it's running on http://localhost:8000")
                                except Exception as e:
                                    st.info(f"💡 Article analyzed successfully! Note: {str(e)}")
                        
                        # Display metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Word Count", f"{data['word_count']:,}")
                        with col2:
                            st.metric("Sentences", data['sentence_count'])
                        with col3:
                            st.metric("Unique Words", f"{data['unique_words']:,}")
                        with col4:
                            st.metric("Vocabulary Richness", f"{data['vocabulary_richness']:.2f}")
                        
                        st.markdown("---")
                        
                        # Text preview
                        st.subheader("📄 Text Preview")
                        st.text_area("Article Content", data['text_preview'], height=150, key="preview")
                        
                        # Two columns for sentiment and keywords
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("😊 Sentiment Analysis")
                            sentiment = data['sentiment']
                            
                            # Sentiment gauge
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number+delta",
                                value=sentiment['polarity'] * 100,
                                title={'text': sentiment['label'].title()},
                                delta={'reference': 0},
                                gauge={
                                    'axis': {'range': [-100, 100]},
                                    'bar': {'color': "darkblue"},
                                    'steps': [
                                        {'range': [-100, -20], 'color': "lightcoral"},
                                        {'range': [-20, 20], 'color': "lightgray"},
                                        {'range': [20, 100], 'color': "lightgreen"}
                                    ],
                                }
                            ))
                            fig.update_layout(height=250)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.markdown(f"""
                            - **Polarity**: {sentiment['polarity']:.2f}
                            - **Confidence**: {sentiment['confidence']:.2f}
                            - **Positive words**: {sentiment['positive_words_found']}
                            - **Negative words**: {sentiment['negative_words_found']}
                            """)
                        
                        with col2:
                            st.subheader("🔑 Top Keywords")
                            keywords_df = pd.DataFrame(data['top_keywords'])
                            
                            if not keywords_df.empty:
                                fig = px.bar(
                                    keywords_df.head(10),
                                    x='count',
                                    y='word',
                                    orientation='h',
                                    title="Most Frequent Words",
                                    labels={'count': 'Frequency', 'word': 'Word'}
                                )
                                fig.update_layout(height=400, showlegend=False)
                                st.plotly_chart(fig, use_container_width=True)
                        
                        # Language statistics
                        st.markdown("---")
                        st.subheader("📊 Language Statistics")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        lang_stats = data['language_stats']
                        with col1:
                            st.metric("Total Tokens", f"{lang_stats['total_tokens']:,}")
                        with col2:
                            st.metric("Content Words", f"{lang_stats['filtered_tokens']:,}")
                        with col3:
                            st.metric("Stopwords Removed", f"{lang_stats['stopwords_removed']:,}")
                        
                        # Pie chart
                        fig = go.Figure(data=[go.Pie(
                            labels=['Content Words', 'Stopwords'],
                            values=[lang_stats['filtered_tokens'], lang_stats['stopwords_removed']],
                            hole=.3
                        )])
                        fig.update_layout(title="Token Distribution", height=300)
                        st.plotly_chart(fig, use_container_width=True)
                        
                    else:
                        st.error(f"❌ {data.get('error', 'Analysis failed')}")
                else:
                    st.error(f"❌ API Error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the API is running on http://localhost:8000")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ==================== PAGE 2: DATABASE ANALYTICS ====================
elif page == "📊 Database Analytics":
    st.header("📊 Database Analytics - Your Saved Articles")
    
    # Add refresh button at the top
    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    with col3:
        auto_refresh = st.checkbox("Auto-refresh", value=False, help="Refresh every 30 seconds")
    
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()
    
    st.markdown("""
    **Comprehensive analysis of all articles in your database:**
    - Articles analyzed from URLs (that you saved)
    - Imported news corpus
    - Trend analysis across categories
    - Sentiment patterns over time
    """)
    
    try:
        # Get stats
        response = requests.get(f"{API_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Terms", f"{stats['terms']:,}", help="Unique Swahili words in database")
            with col2:
                st.metric("Saved Articles", f"{stats['news_articles']:,}", help="Articles available for analysis")
            with col3:
                st.metric("Bantu Classes", stats['bantu_classes'], help="Linguistic classification system")
            
            st.markdown("---")
            
            # Get news articles
            response = requests.get(f"{API_URL}/news/articles?limit=500")
            if response.status_code == 200:
                articles = response.json()
                
                if articles and len(articles) > 0:
                    df = pd.DataFrame(articles)
                    
                    st.success(f"✅ Analyzing {len(articles)} articles from your database")
                    
                    # ===== CONTENT ANALYSIS =====
                    st.subheader("📝 Content Analysis")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        avg_length = df['content'].str.len().mean()
                        st.metric("Avg Article Length", f"{avg_length:.0f} chars")
                    
                    with col2:
                        total_content = df['content'].str.len().sum()
                        st.metric("Total Content", f"{total_content/1000:.1f}K chars")
                    
                    with col3:
                        total_words = df['content'].str.split().str.len().sum()
                        st.metric("Total Words", f"{total_words:,}")
                    
                    with col4:
                        avg_words = df['content'].str.split().str.len().mean()
                        st.metric("Avg Words/Article", f"{avg_words:.0f}")
                    
                    st.markdown("---")
                    
                    # ===== CATEGORY & SENTIMENT ANALYSIS =====
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📚 Distribution by Category")
                        category_counts = df['category'].value_counts()
                        
                        fig = px.pie(
                            values=category_counts.values,
                            names=category_counts.index,
                            title=f"Categories ({len(category_counts)} unique)",
                            hole=0.3
                        )
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Category details
                        category_df = pd.DataFrame({
                            'Category': category_counts.index,
                            'Articles': category_counts.values,
                            'Percentage': (category_counts.values / len(df) * 100).round(1)
                        }).reset_index(drop=True)
                        st.dataframe(category_df, use_container_width=True, height=200)
                    
                    with col2:
                        st.markdown("#### 😊 Sentiment Distribution")
                        
                        if 'sentiment_label' in df.columns and df['sentiment_label'].notna().any():
                            sentiment_counts = df['sentiment_label'].value_counts()
                            
                            fig = px.bar(
                                x=sentiment_counts.index,
                                y=sentiment_counts.values,
                                labels={'x': 'Sentiment', 'y': 'Number of Articles'},
                                color=sentiment_counts.index,
                                color_discrete_map={
                                    'positive': '#4CAF50',
                                    'negative': '#f44336',
                                    'neutral': '#9E9E9E'
                                },
                                title="Sentiment Analysis Results"
                            )
                            fig.update_layout(showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Sentiment details
                            sentiment_df = pd.DataFrame({
                                'Sentiment': sentiment_counts.index,
                                'Count': sentiment_counts.values,
                                'Percentage': (sentiment_counts.values / len(df[df['sentiment_label'].notna()]) * 100).round(1)
                            }).reset_index(drop=True)
                            st.dataframe(sentiment_df, use_container_width=True, height=150)
                        else:
                            st.info("No sentiment data available. Analyze some URLs with sentiment to see this chart!")
                    
                    st.markdown("---")
                    
                    # ===== CATEGORY-SENTIMENT CROSS ANALYSIS =====
                    if 'sentiment_label' in df.columns and df['sentiment_label'].notna().any():
                        st.subheader("🎯 Category-Sentiment Analysis")
                        
                        # Create cross-tabulation
                        cross_tab = pd.crosstab(df['category'], df['sentiment_label'], normalize='index') * 100
                        cross_tab = cross_tab.round(1)
                        
                        # Heatmap
                        fig = px.imshow(
                            cross_tab,
                            labels=dict(x="Sentiment", y="Category", color="Percentage"),
                            x=cross_tab.columns,
                            y=cross_tab.index,
                            color_continuous_scale='RdYlGn',
                            title="Sentiment Distribution by Category (%)"
                        )
                        fig.update_xaxes(side="top")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Which category is most positive/negative?
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if 'positive' in cross_tab.columns:
                                most_positive = cross_tab['positive'].idxmax()
                                st.metric("Most Positive Category", most_positive, 
                                         f"{cross_tab.loc[most_positive, 'positive']:.1f}%")
                        
                        with col2:
                            if 'negative' in cross_tab.columns:
                                most_negative = cross_tab['negative'].idxmax()
                                st.metric("Most Negative Category", most_negative,
                                         f"{cross_tab.loc[most_negative, 'negative']:.1f}%")
                        
                        with col3:
                            if 'neutral' in cross_tab.columns:
                                most_neutral = cross_tab['neutral'].idxmax()
                                st.metric("Most Neutral Category", most_neutral,
                                         f"{cross_tab.loc[most_neutral, 'neutral']:.1f}%")
                    
                    st.markdown("---")
                    
                    # ===== ARTICLES TABLE =====
                    st.subheader("📰 Articles in Database")
                    
                    # Filter options
                    col1, col2 = st.columns(2)
                    with col1:
                        selected_category = st.selectbox(
                            "Filter by category:",
                            ["All"] + list(df['category'].unique())
                        )
                    with col2:
                        selected_sentiment = st.selectbox(
                            "Filter by sentiment:",
                            ["All"] + list(df['sentiment_label'].dropna().unique()) if 'sentiment_label' in df.columns else ["All"]
                        )
                    
                    # Apply filters
                    filtered_df = df.copy()
                    if selected_category != "All":
                        filtered_df = filtered_df[filtered_df['category'] == selected_category]
                    if selected_sentiment != "All" and 'sentiment_label' in df.columns:
                        filtered_df = filtered_df[filtered_df['sentiment_label'] == selected_sentiment]
                    
                    st.write(f"Showing {len(filtered_df)} of {len(df)} articles")
                    
                    # Display table
                    display_df = filtered_df[['category', 'content', 'sentiment_label'] if 'sentiment_label' in filtered_df.columns else ['category', 'content']].head(50).copy()
                    display_df['content'] = display_df['content'].str[:150] + "..."
                    display_df = display_df.rename(columns={
                        'category': 'Category',
                        'content': 'Preview',
                        'sentiment_label': 'Sentiment'
                    })
                    st.dataframe(display_df, use_container_width=True, height=400)
                    
                    # Download option
                    st.markdown("---")
                    st.subheader("📥 Export Data")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download All Articles (CSV)",
                            data=csv,
                            file_name=f"swahili_news_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        # Summary stats JSON
                        summary = {
                            "total_articles": len(df),
                            "categories": category_counts.to_dict(),
                            "sentiment": sentiment_counts.to_dict() if 'sentiment_label' in df.columns else {},
                            "avg_length": float(avg_length),
                            "total_words": int(total_words),
                            "generated_at": datetime.now().isoformat()
                        }
                        st.download_button(
                            label="📊 Download Analysis Summary (JSON)",
                            data=json.dumps(summary, indent=2),
                            file_name=f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                            mime="application/json"
                        )
                
                else:
                    st.info("📭 No articles in database yet!")
                    st.markdown("""
                    ### How to add articles to your database:
                    
                    **Option 1: Analyze URLs** 🔗
                    1. Go to "🔗 URL Analysis" tab
                    2. Paste a Swahili news URL
                    3. ✅ Check "💾 Save to database"
                    4. Click "Analyze"
                    
                    **Option 2: Import News Corpus** 📚
                    ```bash
                    python scripts/03_ingest_news.py
                    ```
                    
                    **Option 3: Import Masakhane Dataset** 📊
                    ```bash
                    python scripts/01_ingest_masakhane.py
                    ```
                    """)
        
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure it's running at http://localhost:8000")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ==================== PAGE 3: SENTIMENT TRENDS ====================
elif page == "📈 Sentiment Trends":
    st.header("📈 Sentiment Trends Over Time")
    
    try:
        response = requests.get(f"{API_URL}/news/trends")
        if response.status_code == 200:
            trends = response.json()
            
            if trends:
                df = pd.DataFrame(trends)
                
                # Area chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['date'], y=df['positive'],
                    name='Positive',
                    line=dict(color='#4CAF50', width=3),
                    fill='tozeroy',
                    stackgroup='one'
                ))
                fig.add_trace(go.Scatter(
                    x=df['date'], y=df['neutral'],
                    name='Neutral',
                    line=dict(color='#9E9E9E', width=3),
                    fill='tonexty',
                    stackgroup='one'
                ))
                fig.add_trace(go.Scatter(
                    x=df['date'], y=df['negative'],
                    name='Negative',
                    line=dict(color='#f44336', width=3),
                    fill='tonexty',
                    stackgroup='one'
                ))
                
                fig.update_layout(
                    title="Sentiment Distribution Over Time",
                    xaxis_title="Date",
                    yaxis_title="Number of Articles",
                    height=500,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_positive = df['positive'].sum()
                    st.metric("Total Positive", f"{total_positive:,}",
                             delta=f"{(total_positive/(df['positive'].sum() + df['negative'].sum() + df['neutral'].sum())*100):.1f}%")
                with col2:
                    total_negative = df['negative'].sum()
                    st.metric("Total Negative", f"{total_negative:,}",
                             delta=f"{(total_negative/(df['positive'].sum() + df['negative'].sum() + df['neutral'].sum())*100):.1f}%")
                with col3:
                    total_neutral = df['neutral'].sum()
                    st.metric("Total Neutral", f"{total_neutral:,}",
                             delta=f"{(total_neutral/(df['positive'].sum() + df['negative'].sum() + df['neutral'].sum())*100):.1f}%")
            else:
                st.info("📊 No trend data available yet. Analyze some articles to see trends!")
                
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API")

# ==================== PAGE 4: LINGUISTIC INSIGHTS ====================
elif page == "🔤 Linguistic Insights":
    st.header("🔤 Advanced Linguistic Analysis")
    
    st.markdown("""
    **Deep dive into Swahili linguistics:**
    - 📊 Lexical Diversity (Type-Token Ratio)
    - 🔤 Morphological Complexity
    - 📏 Word Length Patterns  
    - 🔗 Bigram Analysis
    - 📖 Readability Assessment
    """)
    
    sample_text = st.text_area(
        "Enter Swahili Text (minimum 50 words for best insights)",
        placeholder="Habari za leo ni nzuri sana. Serikali imeahidi kuboresha huduma za afya na elimu...",
        height=150,
        help="Paste at least 50 words for comprehensive linguistic analysis"
    )
    
    # Example text option
    use_example = st.checkbox("📝 Use Example Text", value=False)
    
    if use_example:
        sample_text = st.text_area(
            "Enter Swahili Text (minimum 50 words for best insights)",
            value="Waziri Mkuu wa Tanzania amesema kwamba uchumi wa nchi unaendelea vizuri. Sekta ya utalii imekuwa na mafanikio makubwa mwaka huu. Serikali inaendelea kuwekeza katika miundombinu ya barabara na umeme. Wananchi wanashukuru juhudi za serikali katika kuboresha huduma za afya na elimu. Nchi yetu inaendelea kukua kwa kasi kubwa. Tunatumaini kuona mabadiliko zaidi katika siku zijazo.",
            height=150,
            help="Paste at least 50 words for comprehensive linguistic analysis",
            key="example_text"
        )
    
    analyze_button = st.button("🔬 Analyze Linguistics", type="primary", use_container_width=True)
    
    if analyze_button and sample_text:
        words = sample_text.lower().split()
        
        if len(words) < 10:
            st.warning("⚠️ Please enter at least 10 words for meaningful analysis (50+ recommended)")
        else:
            with st.spinner("Performing deep linguistic analysis..."):
                # === CALCULATE METRICS ===
                unique_words = set(words)
                ttr = len(unique_words) / len(words)
                avg_word_len = sum(len(w) for w in words) / len(words)
                word_lengths = [len(w) for w in words]
                
                # Main metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Words", f"{len(words):,}")
                with col2:
                    st.metric("Unique Words", f"{len(unique_words):,}")
                with col3:
                    st.metric("Lexical Diversity", f"{ttr:.1%}")
                with col4:
                    st.metric("Avg Word Length", f"{avg_word_len:.1f} chars")
                
                st.markdown("---")
                
                # === LEXICAL DIVERSITY & WORD LENGTH ===
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Lexical Diversity (TTR)")
                    
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=ttr * 100,
                        title={'text': "Type-Token Ratio"},
                        number={'suffix': "%"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 30], 'color': "#ffcccc"},
                                {'range': [30, 60], 'color': "#ffffcc"},
                                {'range': [60, 100], 'color': "#ccffcc"}
                            ],
                        }
                    ))
                    fig.update_layout(height=250)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    if ttr > 0.6:
                        st.success("✅ **High diversity** - Rich, varied vocabulary")
                    elif ttr > 0.3:
                        st.info("📝 **Normal diversity** - Typical language use")
                    else:
                        st.warning("⚠️ **Low diversity** - Repetitive text")
                    
                    st.caption(f"Interpretation: {len(unique_words)} unique words out of {len(words)} total")
                
                with col2:
                    st.subheader("📏 Word Length Distribution")
                    
                    fig = px.histogram(
                        x=word_lengths,
                        nbins=max(word_lengths) - min(word_lengths) + 1,
                        labels={'x': 'Word Length (characters)', 'y': 'Frequency'},
                        title="Distribution of Word Lengths"
                    )
                    fig.update_layout(height=300, showlegend=False)
                    fig.update_traces(marker_color='steelblue')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown(f"""
                    **Statistics:**
                    - Shortest: **{min(word_lengths)}** chars
                    - Longest: **{max(word_lengths)}** chars
                    - Median: **{pd.Series(word_lengths).median():.0f}** chars
                    - Mode: **{pd.Series(word_lengths).mode().values[0] if len(pd.Series(word_lengths).mode()) > 0 else 'N/A'}** chars
                    """)
                
                st.markdown("---")
                
                # === BIGRAMS & MORPHOLOGY ===
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🔗 Most Common Bigrams")
                    st.caption("Frequently occurring word pairs")
                    
                    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
                    bigram_counts = Counter(bigrams).most_common(10)
                    
                    if bigram_counts:
                        bigram_df = pd.DataFrame(bigram_counts, columns=['Bigram', 'Frequency'])
                        
                        fig = px.bar(
                            bigram_df,
                            x='Frequency',
                            y='Bigram',
                            orientation='h',
                            title=f"Top {len(bigram_df)} Word Pairs"
                        )
                        fig.update_layout(height=350, showlegend=False)
                        fig.update_traces(marker_color='coral')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Not enough text for bigram analysis")
                
                with col2:
                    st.subheader("🔤 Morphological Patterns")
                    st.caption("Prefix and suffix frequency")
                    
                    # Swahili-specific affixes
                    prefixes = {'ni': 0, 'u': 0, 'a': 0, 'wa': 0, 'ki': 0, 'vi': 0, 'm': 0, 'tu': 0}
                    suffixes = {'a': 0, 'i': 0, 'e': 0, 'o': 0, 'u': 0, 'ni': 0}
                    
                    for word in words:
                        if len(word) > 3:
                            # Check prefixes
                            for p in sorted(prefixes.keys(), key=len, reverse=True):
                                if word.startswith(p):
                                    prefixes[p] += 1
                                    break
                            # Check suffixes
                            for s in sorted(suffixes.keys(), key=len, reverse=True):
                                if word.endswith(s):
                                    suffixes[s] += 1
                                    break
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("**Prefixes:**")
                        top_prefixes = sorted(prefixes.items(), key=lambda x: x[1], reverse=True)[:5]
                        for p, count in top_prefixes:
                            if count > 0:
                                st.write(f"**{p}-**: {count} ({count/len(words)*100:.1f}%)")
                    
                    with col_b:
                        st.markdown("**Suffixes:**")
                        top_suffixes = sorted(suffixes.items(), key=lambda x: x[1], reverse=True)[:5]
                        for s, count in top_suffixes:
                            if count > 0:
                                st.write(f"**-{s}**: {count} ({count/len(words)*100:.1f}%)")
                    
                    # Complexity score
                    complexity = (sum(prefixes.values()) + sum(suffixes.values())) / len(words)
                    st.metric("Morphological Complexity", f"{complexity:.2f}",
                             help="Ratio of detected affixes to total words")
                
                st.markdown("---")
                
                # === READABILITY ASSESSMENT ===
                st.subheader("📖 Readability Assessment")
                
                sentences = max(sample_text.count('.') + sample_text.count('!') + sample_text.count('?'), 1)
                avg_sentence_len = len(words) / sentences
                long_words = [w for w in words if len(w) >= 8]
                complex_ratio = len(long_words) / len(words)
                
                # Simple readability formula
                readability = 100 - (avg_sentence_len * 2) - (complex_ratio * 50)
                readability = max(0, min(100, readability))
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Readability Score", f"{readability:.0f}/100")
                    if readability > 70:
                        st.success("✅ Easy")
                    elif readability > 40:
                        st.info("📝 Moderate")
                    else:
                        st.warning("⚠️ Complex")
                
                with col2:
                    st.metric("Sentences", sentences)
                    st.caption(f"{avg_sentence_len:.1f} words/sentence")
                
                with col3:
                    st.metric("Complex Words", len(long_words))
                    st.caption(f"{complex_ratio:.1%} of total")
                
                with col4:
                    short_words = len([w for w in words if len(w) <= 3])
                    st.metric("Function Words", short_words)
                    st.caption(f"{short_words/len(words):.1%} of total")
                
                # Interpretation
                st.markdown("---")
                st.subheader("📝 Interpretation")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Vocabulary Assessment:**")
                    if ttr > 0.6:
                        st.write("✅ **Excellent** - Sophisticated vocabulary with minimal repetition")
                    elif ttr > 0.4:
                        st.write("📝 **Good** - Balanced vocabulary usage")
                    elif ttr > 0.3:
                        st.write("⚠️ **Fair** - Some repetition present")
                    else:
                        st.write("❌ **Poor** - Highly repetitive text")
                
                with col2:
                    st.markdown("**Complexity Assessment:**")
                    if readability > 70 and avg_sentence_len < 15:
                        st.write("✅ **Simple** - Easy to understand, good for general audience")
                    elif readability > 40 and avg_sentence_len < 20:
                        st.write("📝 **Standard** - Appropriate for educated readers")
                    else:
                        st.write("⚠️ **Advanced** - Requires higher reading level")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Swahili NLP RAG Dashboard | Powered by FastAPI & Streamlit</p>
    <p>📚 16,600+ words | 🏛️ Bantu Classification | 😊 Sentiment Analysis</p>
</div>
""", unsafe_allow_html=True)
