import streamlit as st
import requests
import httpx
import asyncio
from urllib.parse import urlparse
import re
import json
from collections import Counter
import pandas as pd
from typing import List, Dict, Any
import time
import random

# Configure page
st.set_page_config(
    page_title="WebIntel - HTML Analysis Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

class HTMLAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        # Rotate between multiple realistic user agents
        self.user_agents = [
            # Chrome on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            
            # Firefox on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # Chrome on Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Safari on Mac
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebLib/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
            
            # Edge on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            
            # Chrome on Linux
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        # Base headers that will be updated per request
        self.base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
    
    def get_stealth_headers(self):
        """Generate realistic, randomized headers for each request"""
        user_agent = random.choice(self.user_agents)
        headers = self.base_headers.copy()
        headers['User-Agent'] = user_agent
        
        # Add some randomization to headers
        if random.random() > 0.5:
            headers['DNT'] = '1'
        
        # Randomize Accept-Language slightly
        languages = ['en-US,en;q=0.9', 'en-US,en;q=0.9,es;q=0.8', 'en-US,en;q=0.9,fr;q=0.8']
        headers['Accept-Language'] = random.choice(languages)
        
        # Sometimes add referer (as if coming from Google)
        if random.random() > 0.7:
            headers['Referer'] = 'https://www.google.com/'
        
        return headers

    def fetch_html(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Fetch HTML content from URL with advanced anti-detection methods
        """
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Add small random delay to avoid detection
            time.sleep(random.uniform(0.25, 1.0))
            
            # Method 1: Stealth requests with rotating headers
            stealth_headers = self.get_stealth_headers()
            
            # Create a fresh session for each request to avoid tracking
            fresh_session = requests.Session()
            fresh_session.headers.update(stealth_headers)
            
            # Set additional session parameters
            fresh_session.max_redirects = 10
            
            response = fresh_session.get(
                url, 
                timeout=timeout, 
                allow_redirects=True,
                verify=True,  # Keep SSL verification
                stream=False
            )
            response.raise_for_status()
            
            return {
                'success': True,
                'html': response.text,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'url': str(response.url),
                'method': 'stealth_requests'
            }
            
        except requests.exceptions.RequestException as e:
            # Method 2: Try with httpx and different headers
            try:
                stealth_headers = self.get_stealth_headers()
                
                with httpx.Client(
                    timeout=timeout,
                    headers=stealth_headers,
                    follow_redirects=True,
                    verify=True
                ) as client:
                    response = client.get(url)
                    response.raise_for_status()
                    
                    return {
                        'success': True,
                        'html': response.text,
                        'status_code': response.status_code,
                        'headers': dict(response.headers),
                        'url': str(response.url),
                        'method': 'stealth_httpx'
                    }
                    
            except Exception as httpx_error:
                # Method 3: Try with minimal headers (sometimes less is more)
                try:
                    minimal_headers = {
                        'User-Agent': random.choice(self.user_agents),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                    }
                    
                    response = requests.get(
                        url,
                        headers=minimal_headers,
                        timeout=timeout,
                        allow_redirects=True
                    )
                    response.raise_for_status()
                    
                    return {
                        'success': True,
                        'html': response.text,
                        'status_code': response.status_code,
                        'headers': dict(response.headers),
                        'url': str(response.url),
                        'method': 'minimal_headers'
                    }
                    
                except Exception as minimal_error:
                    return {
                        'success': False,
                        'error': f"All methods failed - Primary method: {str(e)} | Secondary method: {str(httpx_error)} | Minimal headers: {str(minimal_error)}",
                        'url': url
                    }
    
    def analyze_html_structure(self, html: str, fetch_result: Dict = None) -> Dict[str, Any]:
        """
        Analyze HTML structure and provide insights
        """
        analysis = {}
        
        # Basic metrics
        analysis['total_length'] = len(html)
        analysis['total_lines'] = len(html.split('\n'))
        
        # Tag analysis
        tags = re.findall(r'<(\w+)[^>]*>', html, re.IGNORECASE)
        tag_counts = Counter(tags)
        analysis['total_tags'] = len(tags)
        analysis['unique_tags'] = len(tag_counts)
        analysis['most_common_tags'] = tag_counts.most_common(10)
        
        # HTML5 semantic tags
        semantic_tags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
        analysis['semantic_tags_used'] = [tag for tag in semantic_tags if tag in tag_counts]
        
        # Meta tags
        meta_tags = re.findall(r'<meta[^>]*>', html, re.IGNORECASE)
        analysis['meta_tags_count'] = len(meta_tags)
        
        # External resources
        analysis['external_css'] = len(re.findall(r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', html, re.IGNORECASE))
        analysis['external_js'] = len(re.findall(r'<script[^>]*src=[^>]*>', html, re.IGNORECASE))
        analysis['inline_css'] = len(re.findall(r'<style[^>]*>.*?</style>', html, re.IGNORECASE | re.DOTALL))
        analysis['inline_js'] = len(re.findall(r'<script[^>]*>.*?</script>', html, re.IGNORECASE | re.DOTALL))
        
        # Images
        img_tags = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
        analysis['images_count'] = len(img_tags)
        
        # Forms
        analysis['forms_count'] = len(re.findall(r'<form[^>]*>', html, re.IGNORECASE))
        
        # Framework detection
        frameworks = self.detect_frameworks(html)
        analysis['frameworks_detected'] = frameworks
        
        # Performance insights
        analysis['performance_insights'] = self.get_performance_insights(analysis)
        
        # New AEO Analysis Dimensions
        current_url = fetch_result.get('url', '') if fetch_result else ''
        analysis.update(self.analyze_html_tables(html))
        analysis.update(self.analyze_atomic_paragraphs(html))
        analysis.update(self.analyze_year_inclusion(html, current_url))
        analysis.update(self.analyze_bulleted_lists(html))
        analysis.update(self.analyze_semantic_urls(current_url, html))
        analysis.update(self.analyze_subfolder_structure(current_url, html))
        analysis.update(self.analyze_html_vs_js(html))
        analysis.update(self.analyze_schema_markup(html))
        analysis.update(self.analyze_h_tags(html))
        
        return analysis
    
    def detect_frameworks(self, html: str) -> List[str]:
        """
        Detect popular frameworks and libraries
        """
        frameworks = []
        
        # React
        if 'react' in html.lower() or 'data-reactroot' in html.lower():
            frameworks.append('React')
        
        # Vue.js
        if 'vue' in html.lower() or 'v-if' in html.lower() or 'v-for' in html.lower():
            frameworks.append('Vue.js')
        
        # Angular
        if 'angular' in html.lower() or 'ng-' in html.lower():
            frameworks.append('Angular')
        
        # jQuery
        if 'jquery' in html.lower():
            frameworks.append('jQuery')
        
        # Bootstrap
        if 'bootstrap' in html.lower():
            frameworks.append('Bootstrap')
        
        # Tailwind CSS
        if 'tailwind' in html.lower() or re.search(r'class="[^"]*\b(flex|grid|bg-|text-|p-|m-)', html):
            frameworks.append('Tailwind CSS')
        
        # WordPress
        if 'wp-content' in html.lower() or 'wordpress' in html.lower():
            frameworks.append('WordPress')
        
        return frameworks
    
    def get_performance_insights(self, analysis: Dict) -> List[str]:
        """
        Generate performance insights based on analysis
        """
        insights = []
        
        if analysis['external_css'] > 5:
            insights.append(f"High number of external CSS files ({analysis['external_css']}) - consider bundling")
        
        if analysis['external_js'] > 10:
            insights.append(f"High number of external JS files ({analysis['external_js']}) - consider bundling")
        
        if analysis['images_count'] > 20:
            insights.append(f"High number of images ({analysis['images_count']}) - consider lazy loading")
        
        if analysis['total_length'] > 1000000:  # 1MB
            insights.append("Large HTML size - consider minification and optimization")
        
        if not analysis['semantic_tags_used']:
            insights.append("No HTML5 semantic tags found - consider improving accessibility")
        
        return insights
    
    def analyze_html_tables(self, html: str) -> Dict[str, Any]:
        """Analyze HTML table structure and data density"""
        table_tags = re.findall(r'<table[^>]*>.*?</table>', html, re.IGNORECASE | re.DOTALL)
        
        analysis = {
            'tables_count': len(table_tags),
            'avg_rows_per_table': 0,
            'table_data_density': 0
        }
        
        if table_tags:
            total_rows = 0
            total_data_cells = 0
            total_cells = 0
            
            for table in table_tags:
                # Count rows
                rows = re.findall(r'<tr[^>]*>', table, re.IGNORECASE)
                total_rows += len(rows)
                
                # Count cells with numeric data
                cells = re.findall(r'<(?:td|th)[^>]*>(.*?)</(?:td|th)>', table, re.IGNORECASE | re.DOTALL)
                total_cells += len(cells)
                
                for cell in cells:
                    # Check if cell contains numeric data
                    if re.search(r'\d+', cell):
                        total_data_cells += 1
            
            analysis['avg_rows_per_table'] = total_rows / len(table_tags)
            analysis['table_data_density'] = total_data_cells / total_cells if total_cells > 0 else 0
        
        return analysis
    
    def analyze_atomic_paragraphs(self, html: str) -> Dict[str, Any]:
        """Analyze paragraph structure for AEO optimization"""
        # Find all paragraph tags
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.IGNORECASE | re.DOTALL)
        
        analysis = {
            'paragraphs_count': len(paragraphs),
            'avg_paragraph_length': 0,
            'atomic_paragraph_ratio': 0
        }
        
        if paragraphs:
            word_counts = []
            atomic_count = 0
            
            for p in paragraphs:
                # Remove HTML tags and count words
                clean_text = re.sub(r'<[^>]+>', '', p)
                words = len(clean_text.split())
                word_counts.append(words)
                
                # Count atomic paragraphs (≤ 100 words)
                if words <= 100:
                    atomic_count += 1
            
            analysis['avg_paragraph_length'] = sum(word_counts) / len(word_counts)
            analysis['atomic_paragraph_ratio'] = atomic_count / len(paragraphs)
        
        return analysis
    
    def analyze_year_inclusion(self, html: str, url: str) -> Dict[str, Any]:
        """Analyze 2025 year inclusion for freshness signals"""
        analysis = {
            'url_year_inclusion': 0,
            'title_year_inclusion': 0,
            'meta_year_inclusion': 0,
            'early_content_year_inclusion': 0
        }
        
        # URL year inclusion
        if url and '2025' in url:
            analysis['url_year_inclusion'] = 1
        
        # Title year inclusion
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if title_match and '2025' in title_match.group(1):
            analysis['title_year_inclusion'] = 1
        
        # Meta description year inclusion
        meta_desc = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
        if meta_desc and '2025' in meta_desc.group(1):
            analysis['meta_year_inclusion'] = 1
        
        # First 200 characters of visible text
        # Remove script and style content
        clean_html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
        clean_html = re.sub(r'<style[^>]*>.*?</style>', '', clean_html, flags=re.IGNORECASE | re.DOTALL)
        
        # Extract visible text
        visible_text = re.sub(r'<[^>]+>', '', clean_html)
        visible_text = re.sub(r'\s+', ' ', visible_text).strip()
        
        if len(visible_text) >= 200 and '2025' in visible_text[:200]:
            analysis['early_content_year_inclusion'] = 1
        
        return analysis
    
    def analyze_bulleted_lists(self, html: str) -> Dict[str, Any]:
        """Analyze list structures for snippet optimization"""
        ul_lists = re.findall(r'<ul[^>]*>.*?</ul>', html, re.IGNORECASE | re.DOTALL)
        ol_lists = re.findall(r'<ol[^>]*>.*?</ol>', html, re.IGNORECASE | re.DOTALL)
        all_lists = ul_lists + ol_lists
        
        # Count paragraphs for coverage ratio
        paragraphs = re.findall(r'<p[^>]*>', html, re.IGNORECASE)
        
        analysis = {
            'lists_count': len(all_lists),
            'avg_items_per_list': 0,
            'list_coverage_ratio': 0
        }
        
        if all_lists:
            total_items = 0
            
            for list_html in all_lists:
                items = re.findall(r'<li[^>]*>', list_html, re.IGNORECASE)
                total_items += len(items)
            
            analysis['avg_items_per_list'] = total_items / len(all_lists)
            analysis['list_coverage_ratio'] = total_items / (len(paragraphs) + total_items) if (len(paragraphs) + total_items) > 0 else 0
        
        return analysis
    
    def analyze_semantic_urls(self, url: str, html: str) -> Dict[str, Any]:
        """Analyze URL semantic structure"""
        analysis = {
            'url_token_count': 0,
            'keyword_presence_ratio': 0,
            'stopword_ratio': 0
        }
        
        if not url:
            return analysis
        
        # Parse URL path
        parsed_url = urlparse(url)
        path = parsed_url.path.strip('/')
        
        if path:
            # Split on common separators
            tokens = re.split(r'[-_/]+', path)
            tokens = [t for t in tokens if t]  # Remove empty tokens
            
            analysis['url_token_count'] = len(tokens)
            
            if tokens:
                # Get H2/H3 keywords for comparison
                h2_h3_text = ''
                h2_matches = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html, re.IGNORECASE | re.DOTALL)
                for match in h2_matches:
                    h2_h3_text += re.sub(r'<[^>]+>', '', match).lower() + ' '
                
                # Count keyword matches
                keyword_matches = 0
                for token in tokens:
                    if token.lower() in h2_h3_text:
                        keyword_matches += 1
                
                analysis['keyword_presence_ratio'] = keyword_matches / len(tokens)
                
                # Count stopwords
                stopwords = {'and', 'the', 'of', 'to', 'a', 'in', 'for', 'is', 'on', 'with', 'as', 'by', 'at', 'or', 'an'}
                stopword_count = sum(1 for token in tokens if token.lower() in stopwords)
                analysis['stopword_ratio'] = stopword_count / len(tokens)
        
        return analysis
    
    def analyze_subfolder_structure(self, url: str, html: str) -> Dict[str, Any]:
        """Analyze subfolder organization and depth"""
        analysis = {
            'subfolder_page_ratio': 0,
            'url_depth': 0,
            'deep_link_density': 0,
            'most_common_subfolder': ''
        }
        
        if not url:
            return analysis
        
        parsed_url = urlparse(url)
        path_segments = [s for s in parsed_url.path.split('/') if s]
        
        analysis['url_depth'] = len(path_segments)
        analysis['subfolder_page_ratio'] = 1 if len(path_segments) >= 2 else 0
        
        if path_segments:
            analysis['most_common_subfolder'] = path_segments[0]
        
        # Analyze internal links depth
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        internal_links = re.findall(rf'href=["\']({re.escape(domain)}[^"\']*)["\']', html, re.IGNORECASE)
        
        if internal_links:
            deep_links = 0
            for link in internal_links:
                link_path = urlparse(link).path
                link_segments = [s for s in link_path.split('/') if s]
                if len(link_segments) >= 2:
                    deep_links += 1
            
            analysis['deep_link_density'] = deep_links / len(internal_links)
        
        return analysis
    
    def analyze_html_vs_js(self, html: str) -> Dict[str, Any]:
        """Analyze HTML vs JavaScript content balance"""
        # Calculate HTML content size
        html_size = len(html.encode('utf-8'))
        
        # Find and calculate JavaScript content size
        js_content = re.findall(r'<script[^>]*>(.*?)</script>', html, re.IGNORECASE | re.DOTALL)
        js_size = sum(len(js.encode('utf-8')) for js in js_content)
        
        # Count external JS references
        external_js = re.findall(r'<script[^>]*src=[^>]*>', html, re.IGNORECASE)
        
        # Count script tag hooks
        script_tags = re.findall(r'<script[^>]*>', html, re.IGNORECASE)
        total_tags = len(re.findall(r'<[^>]+>', html))
        
        analysis = {
            'html_js_byte_ratio': html_size / (html_size + js_size) if (html_size + js_size) > 0 else 1,
            'script_tag_density': len(script_tags) / total_tags if total_tags > 0 else 0,
            'external_js_count': len(external_js),
            'inline_js_size': js_size
        }
        
        return analysis
    
    def analyze_schema_markup(self, html: str) -> Dict[str, Any]:
        """Analyze Schema.org structured data"""
        # Find JSON-LD blocks
        jsonld_blocks = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', 
                                  html, re.IGNORECASE | re.DOTALL)
        
        analysis = {
            'schema_blocks_count': len(jsonld_blocks),
            'jsonld_blocks_count': len(jsonld_blocks),
            'schema_types': [],
            'schema_type_count': 0
        }
        
        schema_types = set()
        
        for block in jsonld_blocks:
            try:
                data = json.loads(block.strip())
                
                # Handle both single objects and arrays
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and '@type' in item:
                            schema_types.add(item['@type'])
                elif isinstance(data, dict) and '@type' in data:
                    schema_types.add(data['@type'])
                    
            except json.JSONDecodeError:
                continue
        
        analysis['schema_types'] = list(schema_types)
        analysis['schema_type_count'] = len(schema_types)
        
        return analysis
    
    def analyze_h_tags(self, html: str) -> Dict[str, Any]:
        """Analyze heading tag structure for AEO"""
        h2_tags = re.findall(r'<h2[^>]*>', html, re.IGNORECASE)
        h3_tags = re.findall(r'<h3[^>]*>', html, re.IGNORECASE)
        
        # Count content blocks (paragraphs and div elements that could be content)
        paragraphs = re.findall(r'<p[^>]*>', html, re.IGNORECASE)
        content_divs = re.findall(r'<div[^>]*class=[^>]*(?:content|text|article)[^>]*>', html, re.IGNORECASE)
        total_content_blocks = len(paragraphs) + len(content_divs)
        
        # Count paragraphs that follow H2/H3 tags
        # This is a simplified approach - we'll count H2/H3 tags as proxies
        headings_count = len(h2_tags) + len(h3_tags)
        
        analysis = {
            'h2_count': len(h2_tags),
            'h3_count': len(h3_tags),
            'heading_coverage_ratio': headings_count / total_content_blocks if total_content_blocks > 0 else 0
        }
        
        return analysis

def main():
    st.title("🔍 WebIntel - AEO HTML Analysis Tool")
    st.markdown("Analyze website HTML structure with focus on **Answer Engine Optimization (AEO)** best practices")
    
    # Add AEO explanation
    with st.expander("🎯 What is Answer Engine Optimization (AEO)?"):
        st.markdown("""
        **Answer Engine Optimization (AEO)** is the practice of optimizing content for AI-powered answer engines 
        like ChatGPT, Claude, Perplexity, and Google's AI overviews. Unlike traditional SEO, AEO focuses on:
        
        - **Atomic Paragraphs**: Short, self-contained answers (≤100 words)
        - **Structured Data**: Schema markup for better content understanding
        - **Table & List Optimization**: Data that can be easily parsed into snippets
        - **Semantic URLs**: Clear, keyword-rich paths
        - **Freshness Signals**: Current year inclusion for topical relevance
        - **HTML-First Content**: Server-side rendering over client-side JavaScript
        """)
    
    # Analysis Mode Selection
    st.header("📊 Analysis Mode")
    analysis_mode = st.radio(
        "Choose your analysis mode:",
        ["🔍 Single Analysis", "⚔️ Head-to-Head Comparison"],
        help="Single Analysis: Analyze one set of URLs. Head-to-Head: Compare two sets of URLs against each other."
    )
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        timeout = st.slider("Request Timeout (seconds)", 5, 60, 15)
        max_urls = st.number_input("Max URLs to process per group", 1, 50, 10)
        
        st.subheader("🌐 Request Settings")
        st.info("Advanced request features:")
        st.write("✅ Rotating User Agents (11 different browsers)")
        st.write("✅ Randomized Headers")
        st.write("✅ Random Delays (0.5-2.0s)")
        st.write("✅ Fresh Sessions per Request")
        st.write("✅ Multiple Fallback Methods")
        
        stealth_delay = st.checkbox("Additional Delays", value=False, help="Add longer random delays between requests (2-5 seconds)")
        
        if stealth_delay:
            st.warning("⏱️ Extra delays enabled - analysis will be slower")
    
    if analysis_mode == "🔍 Single Analysis":
        run_single_analysis(timeout, max_urls, stealth_delay)
    else:
        run_head_to_head_analysis(timeout, max_urls, stealth_delay)

def run_single_analysis(timeout: int, max_urls: int, stealth_delay: bool):
    """Run single URL set analysis"""
    # URL input section
    st.header("1. Enter URLs to Analyze")
    
    # Option 1: Text area for multiple URLs
    urls_text = st.text_area(
        "Enter URLs (one per line):",
        placeholder="https://example.com\nhttps://google.com\nhttps://github.com",
        height=150
    )
    
    # Option 2: File upload
    uploaded_file = st.file_uploader("Or upload a text file with URLs", type=['txt', 'csv'])
    
    if uploaded_file is not None:
        content = uploaded_file.read().decode('utf-8')
        urls_text = content
    
    # Process URLs
    if st.button("🚀 Analyze URLs", type="primary"):
        results = analyze_url_list(urls_text, max_urls, timeout, "Analyzing URLs", stealth_delay)
        
        if results:
            display_results(results)

def run_head_to_head_analysis(timeout: int, max_urls: int, stealth_delay: bool):
    """Run head-to-head comparison analysis"""
    st.header("1. Enter URLs for Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔵 Group A (e.g., Your Site)")
        urls_a_text = st.text_area(
            "Enter Group A URLs (one per line):",
            placeholder="https://yoursite.com/page1\nhttps://yoursite.com/page2",
            height=150,
            key="urls_a"
        )
        
        uploaded_file_a = st.file_uploader("Or upload Group A URLs", type=['txt', 'csv'], key="file_a")
        if uploaded_file_a is not None:
            content = uploaded_file_a.read().decode('utf-8')
            urls_a_text = content
    
    with col2:
        st.subheader("🔴 Group B (e.g., Competitor)")
        urls_b_text = st.text_area(
            "Enter Group B URLs (one per line):",
            placeholder="https://competitor.com/page1\nhttps://competitor.com/page2",
            height=150,
            key="urls_b"
        )
        
        uploaded_file_b = st.file_uploader("Or upload Group B URLs", type=['txt', 'csv'], key="file_b")
        if uploaded_file_b is not None:
            content = uploaded_file_b.read().decode('utf-8')
            urls_b_text = content
    
    # Process comparison
    if st.button("⚔️ Compare Groups", type="primary"):
        if not urls_a_text.strip() or not urls_b_text.strip():
            st.error("Please enter URLs for both groups")
            return
        
        # Analyze both groups
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("🔵 Analyzing Group A...")
            results_a = analyze_url_list(urls_a_text, max_urls, timeout, "Group A", stealth_delay)
        
        with col2:
            st.info("🔴 Analyzing Group B...")
            results_b = analyze_url_list(urls_b_text, max_urls, timeout, "Group B", stealth_delay)
        
        if results_a and results_b:
            display_head_to_head_results(results_a, results_b)

def analyze_url_list(urls_text: str, max_urls: int, timeout: int, group_name: str, stealth_delay: bool = False) -> List[Dict]:
    """Analyze a list of URLs and return results"""
    # Parse URLs
    urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
    urls = urls[:max_urls]  # Limit number of URLs
    
    if not urls:
        st.error(f"No valid URLs found for {group_name}")
        return []
    
    analyzer = HTMLAnalyzer()
    results = []
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, url in enumerate(urls):
        status_text.text(f"Processing {group_name} {i+1}/{len(urls)}: {url}")
        progress_bar.progress((i + 1) / len(urls))
        
        # Add extra delay if enabled
        if stealth_delay and i > 0:  # Don't delay the first request
            extra_delay = random.uniform(2.0, 5.0)
            status_text.text(f"⏱️ Additional delay ({extra_delay:.1f}s) - Processing {group_name} {i+1}/{len(urls)}: {url}")
            time.sleep(extra_delay)
        
        # Fetch and analyze
        fetch_result = analyzer.fetch_html(url, timeout)
        
        if fetch_result['success']:
            analysis = analyzer.analyze_html_structure(fetch_result['html'], fetch_result)
            analysis['url'] = url
            analysis['status_code'] = fetch_result['status_code']
            analysis['method'] = fetch_result['method']
            analysis['final_url'] = fetch_result['url']
            results.append(analysis)
        else:
            st.error(f"Failed to fetch {url}: {fetch_result['error']}")
    
    status_text.text(f"{group_name} analysis complete!")
    progress_bar.progress(1.0)
    
    return results

def calculate_group_averages(results: List[Dict]) -> Dict[str, float]:
    """Calculate average metrics for a group of results"""
    if not results:
        return {}
    
    n = len(results)
    averages = {
        # Basic metrics
        'html_size_kb': sum(r['total_length'] for r in results) / n / 1024,
        'total_tags': sum(r['total_tags'] for r in results) / n,
        'unique_tags': sum(r['unique_tags'] for r in results) / n,
        
        # AEO metrics
        'paragraphs_count': sum(r.get('paragraphs_count', 0) for r in results) / n,
        'avg_paragraph_length': sum(r.get('avg_paragraph_length', 0) for r in results) / n,
        'atomic_paragraph_ratio': sum(r.get('atomic_paragraph_ratio', 0) for r in results) / n,
        'h2_count': sum(r.get('h2_count', 0) for r in results) / n,
        'h3_count': sum(r.get('h3_count', 0) for r in results) / n,
        'heading_coverage_ratio': sum(r.get('heading_coverage_ratio', 0) for r in results) / n,
        
        # Freshness signals
        'url_year_inclusion': sum(r.get('url_year_inclusion', 0) for r in results) / n,
        'title_year_inclusion': sum(r.get('title_year_inclusion', 0) for r in results) / n,
        'meta_year_inclusion': sum(r.get('meta_year_inclusion', 0) for r in results) / n,
        'early_content_year_inclusion': sum(r.get('early_content_year_inclusion', 0) for r in results) / n,
        
        # Tables and lists
        'tables_count': sum(r.get('tables_count', 0) for r in results) / n,
        'avg_rows_per_table': sum(r.get('avg_rows_per_table', 0) for r in results) / n,
        'table_data_density': sum(r.get('table_data_density', 0) for r in results) / n,
        'lists_count': sum(r.get('lists_count', 0) for r in results) / n,
        'avg_items_per_list': sum(r.get('avg_items_per_list', 0) for r in results) / n,
        'list_coverage_ratio': sum(r.get('list_coverage_ratio', 0) for r in results) / n,
        
        # URL and structure
        'url_depth': sum(r.get('url_depth', 0) for r in results) / n,
        'url_token_count': sum(r.get('url_token_count', 0) for r in results) / n,
        'keyword_presence_ratio': sum(r.get('keyword_presence_ratio', 0) for r in results) / n,
        'stopword_ratio': sum(r.get('stopword_ratio', 0) for r in results) / n,
        'deep_link_density': sum(r.get('deep_link_density', 0) for r in results) / n,
        
        # Technical
        'html_js_byte_ratio': sum(r.get('html_js_byte_ratio', 1) for r in results) / n,
        'script_tag_density': sum(r.get('script_tag_density', 0) for r in results) / n,
        'external_js_count': sum(r.get('external_js_count', 0) for r in results) / n,
        'inline_js_size_kb': sum(r.get('inline_js_size', 0) for r in results) / n / 1024,
        
        # Schema
        'schema_blocks_count': sum(r.get('schema_blocks_count', 0) for r in results) / n,
        'schema_type_count': sum(r.get('schema_type_count', 0) for r in results) / n,
        
        # Resources
        'external_css': sum(r.get('external_css', 0) for r in results) / n,
        'external_js': sum(r.get('external_js', 0) for r in results) / n,
        'images_count': sum(r.get('images_count', 0) for r in results) / n,
        'forms_count': sum(r.get('forms_count', 0) for r in results) / n,
    }
    
    return averages

def display_head_to_head_results(results_a: List[Dict], results_b: List[Dict]):
    """Display head-to-head comparison results"""
    st.header("⚔️ Head-to-Head Comparison Results")
    
    # Calculate averages
    avg_a = calculate_group_averages(results_a)
    avg_b = calculate_group_averages(results_b)
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔵 Group A URLs", len(results_a))
    with col2:
        st.metric("🔴 Group B URLs", len(results_b))
    with col3:
        # Calculate overall winner
        wins_a = 0
        total_comparisons = 0
        
        key_metrics = [
            'atomic_paragraph_ratio', 'heading_coverage_ratio', 'schema_blocks_count',
            'html_js_byte_ratio', 'table_data_density', 'list_coverage_ratio'
        ]
        
        for metric in key_metrics:
            if metric in avg_a and metric in avg_b:
                total_comparisons += 1
                if avg_a[metric] > avg_b[metric]:
                    wins_a += 1
        
        if total_comparisons > 0:
            winner = "🔵 Group A" if wins_a > total_comparisons/2 else "🔴 Group B" if wins_a < total_comparisons/2 else "🤝 Tie"
            st.metric("🏆 Overall Winner", winner)
    
    # Detailed comparison table
    st.subheader("📊 Detailed Metrics Comparison")
    
    comparison_data = []
    
    # AEO Metrics
    comparison_data.extend([
        ("📝 Content Structure", "", "", ""),
        ("Paragraphs Count", f"{avg_a.get('paragraphs_count', 0):.1f}", f"{avg_b.get('paragraphs_count', 0):.1f}", get_winner_indicator(avg_a.get('paragraphs_count', 0), avg_b.get('paragraphs_count', 0), higher_better=True)),
        ("Avg Paragraph Length", f"{avg_a.get('avg_paragraph_length', 0):.1f} words", f"{avg_b.get('avg_paragraph_length', 0):.1f} words", get_winner_indicator(avg_a.get('avg_paragraph_length', 0), avg_b.get('avg_paragraph_length', 0), higher_better=False)),
        ("Atomic Paragraph Ratio", f"{avg_a.get('atomic_paragraph_ratio', 0):.2f}", f"{avg_b.get('atomic_paragraph_ratio', 0):.2f}", get_winner_indicator(avg_a.get('atomic_paragraph_ratio', 0), avg_b.get('atomic_paragraph_ratio', 0), higher_better=True)),
        ("H2 Tags", f"{avg_a.get('h2_count', 0):.1f}", f"{avg_b.get('h2_count', 0):.1f}", get_winner_indicator(avg_a.get('h2_count', 0), avg_b.get('h2_count', 0), higher_better=True)),
        ("H3 Tags", f"{avg_a.get('h3_count', 0):.1f}", f"{avg_b.get('h3_count', 0):.1f}", get_winner_indicator(avg_a.get('h3_count', 0), avg_b.get('h3_count', 0), higher_better=True)),
        ("Heading Coverage", f"{avg_a.get('heading_coverage_ratio', 0):.2f}", f"{avg_b.get('heading_coverage_ratio', 0):.2f}", get_winner_indicator(avg_a.get('heading_coverage_ratio', 0), avg_b.get('heading_coverage_ratio', 0), higher_better=True)),
        
        ("🗓️ 2025 Freshness Signals", "", "", ""),
        ("URL Year Inclusion", f"{avg_a.get('url_year_inclusion', 0):.0%}", f"{avg_b.get('url_year_inclusion', 0):.0%}", get_winner_indicator(avg_a.get('url_year_inclusion', 0), avg_b.get('url_year_inclusion', 0), higher_better=True)),
        ("Title Year Inclusion", f"{avg_a.get('title_year_inclusion', 0):.0%}", f"{avg_b.get('title_year_inclusion', 0):.0%}", get_winner_indicator(avg_a.get('title_year_inclusion', 0), avg_b.get('title_year_inclusion', 0), higher_better=True)),
        ("Meta Year Inclusion", f"{avg_a.get('meta_year_inclusion', 0):.0%}", f"{avg_b.get('meta_year_inclusion', 0):.0%}", get_winner_indicator(avg_a.get('meta_year_inclusion', 0), avg_b.get('meta_year_inclusion', 0), higher_better=True)),
        ("Early Content Year", f"{avg_a.get('early_content_year_inclusion', 0):.0%}", f"{avg_b.get('early_content_year_inclusion', 0):.0%}", get_winner_indicator(avg_a.get('early_content_year_inclusion', 0), avg_b.get('early_content_year_inclusion', 0), higher_better=True)),
        
        ("📊 Tables & Lists", "", "", ""),
        ("Tables Count", f"{avg_a.get('tables_count', 0):.1f}", f"{avg_b.get('tables_count', 0):.1f}", get_winner_indicator(avg_a.get('tables_count', 0), avg_b.get('tables_count', 0), higher_better=True)),
        ("Table Data Density", f"{avg_a.get('table_data_density', 0):.2f}", f"{avg_b.get('table_data_density', 0):.2f}", get_winner_indicator(avg_a.get('table_data_density', 0), avg_b.get('table_data_density', 0), higher_better=True)),
        ("Lists Count", f"{avg_a.get('lists_count', 0):.1f}", f"{avg_b.get('lists_count', 0):.1f}", get_winner_indicator(avg_a.get('lists_count', 0), avg_b.get('lists_count', 0), higher_better=True)),
        ("List Coverage Ratio", f"{avg_a.get('list_coverage_ratio', 0):.2f}", f"{avg_b.get('list_coverage_ratio', 0):.2f}", get_winner_indicator(avg_a.get('list_coverage_ratio', 0), avg_b.get('list_coverage_ratio', 0), higher_better=True)),
        
        ("🔗 URL Structure", "", "", ""),
        ("URL Depth", f"{avg_a.get('url_depth', 0):.1f}", f"{avg_b.get('url_depth', 0):.1f}", get_winner_indicator(avg_a.get('url_depth', 0), avg_b.get('url_depth', 0), higher_better=True)),
        ("URL Token Count", f"{avg_a.get('url_token_count', 0):.1f}", f"{avg_b.get('url_token_count', 0):.1f}", get_winner_indicator(avg_a.get('url_token_count', 0), avg_b.get('url_token_count', 0), higher_better=True)),
        ("Keyword Presence", f"{avg_a.get('keyword_presence_ratio', 0):.2f}", f"{avg_b.get('keyword_presence_ratio', 0):.2f}", get_winner_indicator(avg_a.get('keyword_presence_ratio', 0), avg_b.get('keyword_presence_ratio', 0), higher_better=True)),
        ("Stopword Ratio", f"{avg_a.get('stopword_ratio', 0):.2f}", f"{avg_b.get('stopword_ratio', 0):.2f}", get_winner_indicator(avg_a.get('stopword_ratio', 0), avg_b.get('stopword_ratio', 0), higher_better=False)),
        
        ("⚡ Technical Performance", "", "", ""),
        ("HTML/JS Ratio", f"{avg_a.get('html_js_byte_ratio', 1):.2f}", f"{avg_b.get('html_js_byte_ratio', 1):.2f}", get_winner_indicator(avg_a.get('html_js_byte_ratio', 1), avg_b.get('html_js_byte_ratio', 1), higher_better=True)),
        ("Script Tag Density", f"{avg_a.get('script_tag_density', 0):.3f}", f"{avg_b.get('script_tag_density', 0):.3f}", get_winner_indicator(avg_a.get('script_tag_density', 0), avg_b.get('script_tag_density', 0), higher_better=False)),
        ("External JS Files", f"{avg_a.get('external_js_count', 0):.1f}", f"{avg_b.get('external_js_count', 0):.1f}", get_winner_indicator(avg_a.get('external_js_count', 0), avg_b.get('external_js_count', 0), higher_better=False)),
        
        ("📱 Schema & Resources", "", "", ""),
        ("Schema Blocks", f"{avg_a.get('schema_blocks_count', 0):.1f}", f"{avg_b.get('schema_blocks_count', 0):.1f}", get_winner_indicator(avg_a.get('schema_blocks_count', 0), avg_b.get('schema_blocks_count', 0), higher_better=True)),
        ("Schema Types", f"{avg_a.get('schema_type_count', 0):.1f}", f"{avg_b.get('schema_type_count', 0):.1f}", get_winner_indicator(avg_a.get('schema_type_count', 0), avg_b.get('schema_type_count', 0), higher_better=True)),
        ("HTML Size", f"{avg_a.get('html_size_kb', 0):.1f} KB", f"{avg_b.get('html_size_kb', 0):.1f} KB", get_winner_indicator(avg_a.get('html_size_kb', 0), avg_b.get('html_size_kb', 0), higher_better=False)),
        ("Images Count", f"{avg_a.get('images_count', 0):.1f}", f"{avg_b.get('images_count', 0):.1f}", get_winner_indicator(avg_a.get('images_count', 0), avg_b.get('images_count', 0), higher_better=False, threshold=20)),
    ])
    
    # Create dataframe
    df_comparison = pd.DataFrame(comparison_data, columns=['Metric', '🔵 Group A', '🔴 Group B', 'Winner'])
    
    # Display with styling
    st.dataframe(
        df_comparison,
        use_container_width=True,
        hide_index=True
    )
    
    # Key insights
    st.subheader("🎯 Key Insights")
    
    insights = []
    
    # AEO insights
    if avg_a.get('atomic_paragraph_ratio', 0) > avg_b.get('atomic_paragraph_ratio', 0):
        insights.append("🔵 Group A has better atomic paragraph structure for answer engines")
    elif avg_b.get('atomic_paragraph_ratio', 0) > avg_a.get('atomic_paragraph_ratio', 0):
        insights.append("🔴 Group B has better atomic paragraph structure for answer engines")
    
    # Freshness insights
    freshness_a = (avg_a.get('url_year_inclusion', 0) + avg_a.get('title_year_inclusion', 0) + 
                   avg_a.get('meta_year_inclusion', 0) + avg_a.get('early_content_year_inclusion', 0)) / 4
    freshness_b = (avg_b.get('url_year_inclusion', 0) + avg_b.get('title_year_inclusion', 0) + 
                   avg_b.get('meta_year_inclusion', 0) + avg_b.get('early_content_year_inclusion', 0)) / 4
    
    if freshness_a > freshness_b:
        insights.append("🔵 Group A shows stronger 2025 freshness signals")
    elif freshness_b > freshness_a:
        insights.append("🔴 Group B shows stronger 2025 freshness signals")
    
    # Schema insights
    if avg_a.get('schema_blocks_count', 0) > avg_b.get('schema_blocks_count', 0):
        insights.append("🔵 Group A has better structured data implementation")
    elif avg_b.get('schema_blocks_count', 0) > avg_a.get('schema_blocks_count', 0):
        insights.append("🔴 Group B has better structured data implementation")
    
    # Technical insights
    if avg_a.get('html_js_byte_ratio', 1) > avg_b.get('html_js_byte_ratio', 1):
        insights.append("🔵 Group A is more AEO-friendly with better HTML/JS balance")
    elif avg_b.get('html_js_byte_ratio', 1) > avg_a.get('html_js_byte_ratio', 1):
        insights.append("🔴 Group B is more AEO-friendly with better HTML/JS balance")
    
    if insights:
        for insight in insights:
            st.write(f"• {insight}")
    else:
        st.write("• Both groups show similar AEO performance across key metrics")

def get_winner_indicator(val_a: float, val_b: float, higher_better: bool = True, threshold: float = None) -> str:
    """Return winner indicator for comparison"""
    if val_a == val_b:
        return "🤝"
    
    if threshold is not None:
        # For metrics where there's an optimal range
        diff_a = abs(val_a - threshold)
        diff_b = abs(val_b - threshold)
        return "🔵" if diff_a < diff_b else "🔴"
    
    if higher_better:
        return "🔵" if val_a > val_b else "🔴"
    else:
        return "🔵" if val_a < val_b else "🔴"

def display_results(results: List[Dict]):
    """Display analysis results in organized tabs"""
    
    # Summary statistics
    st.subheader("📊 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("URLs Analyzed", len(results))
    with col2:
        avg_size = sum(r['total_length'] for r in results) / len(results) if results else 0
        st.metric("Avg HTML Size", f"{avg_size/1024:.1f} KB")
    with col3:
        total_tags = sum(r['total_tags'] for r in results)
        st.metric("Total HTML Tags", total_tags)
    with col4:
        frameworks = set()
        for r in results:
            frameworks.update(r['frameworks_detected'])
        st.metric("Frameworks Found", len(frameworks))
    
    # AEO Analysis tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏗️ Structure Overview", 
        "🎯 AEO Analysis", 
        "📊 Tables & Lists", 
        "🔗 URLs & Links", 
        "⚡ Performance", 
        "📱 Frameworks & Schema"
    ])
    
    with tab1:
        st.subheader("HTML Structure Overview")
        
        # Create basic comparison dataframe
        comparison_data = []
        for result in results:
            comparison_data.append({
                'URL': result['url'][:40] + '...' if len(result['url']) > 40 else result['url'],
                'HTML Size (KB)': f"{result['total_length']/1024:.1f}",
                'Total Tags': result['total_tags'],
                'Paragraphs': result.get('paragraphs_count', 0),
                'Tables': result.get('tables_count', 0),
                'Lists': result.get('lists_count', 0),
                'H2+H3': result.get('h2_count', 0) + result.get('h3_count', 0),
                'Schema Types': result.get('schema_type_count', 0)
            })
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)
    
    with tab2:
        st.subheader("🎯 Answer Engine Optimization (AEO) Analysis")
        
        # AEO Summary Metrics
        st.write("### 📈 AEO Performance Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_atomic_ratio = sum(r.get('atomic_paragraph_ratio', 0) for r in results) / len(results)
            st.metric("Avg Atomic Paragraph Ratio", f"{avg_atomic_ratio:.2f}", help="Paragraphs ≤100 words (target: ≥0.8)")
        
        with col2:
            year_urls = sum(r.get('url_year_inclusion', 0) for r in results)
            st.metric("URLs with 2025", f"{year_urls}/{len(results)}", help="URLs containing '2025' for freshness")
        
        with col3:
            avg_heading_coverage = sum(r.get('heading_coverage_ratio', 0) for r in results) / len(results)
            st.metric("Avg Heading Coverage", f"{avg_heading_coverage:.2f}", help="Content blocks with H2/H3 structure")
        
        with col4:
            schema_pages = sum(1 for r in results if r.get('schema_blocks_count', 0) > 0)
            st.metric("Pages with Schema", f"{schema_pages}/{len(results)}", help="Pages with structured data")
        
        # Detailed AEO Analysis per URL
        st.write("### 📋 Detailed AEO Analysis")
        for i, result in enumerate(results):
            with st.expander(f"🎯 {result['url']}", expanded=i == 0):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**📝 Content Structure:**")
                    st.write(f"- Paragraphs: {result.get('paragraphs_count', 0)}")
                    st.write(f"- Avg Paragraph Length: {result.get('avg_paragraph_length', 0):.1f} words")
                    st.write(f"- Atomic Ratio: {result.get('atomic_paragraph_ratio', 0):.2f} {'✅' if result.get('atomic_paragraph_ratio', 0) >= 0.8 else '⚠️'}")
                    st.write(f"- H2 Tags: {result.get('h2_count', 0)}")
                    st.write(f"- H3 Tags: {result.get('h3_count', 0)}")
                    st.write(f"- Heading Coverage: {result.get('heading_coverage_ratio', 0):.2f}")
                
                with col2:
                    st.write("**🗓️ Freshness Signals (2025):**")
                    st.write(f"- URL: {'✅' if result.get('url_year_inclusion', 0) else '❌'}")
                    st.write(f"- Title: {'✅' if result.get('title_year_inclusion', 0) else '❌'}")
                    st.write(f"- Meta Description: {'✅' if result.get('meta_year_inclusion', 0) else '❌'}")
                    st.write(f"- Early Content: {'✅' if result.get('early_content_year_inclusion', 0) else '❌'}")
                    
                    st.write("**🔗 Technical SEO:**")
                    st.write(f"- Schema Blocks: {result.get('schema_blocks_count', 0)}")
                    if result.get('schema_types'):
                        st.write(f"- Schema Types: {', '.join(result['schema_types'])}")
    
    with tab3:
        st.subheader("📊 Tables & Lists Analysis")
        
        # Tables Analysis
        st.write("### 📋 Tables")
        table_data = []
        for result in results:
            table_data.append({
                'URL': result['url'][:40] + '...' if len(result['url']) > 40 else result['url'],
                'Tables': result.get('tables_count', 0),
                'Avg Rows/Table': f"{result.get('avg_rows_per_table', 0):.1f}",
                'Data Density': f"{result.get('table_data_density', 0):.2f}",
                'Assessment': '✅ Good' if result.get('table_data_density', 0) > 0.5 else '⚠️ Low' if result.get('tables_count', 0) > 0 else '📝 None'
            })
        
        df_tables = pd.DataFrame(table_data)
        st.dataframe(df_tables, use_container_width=True)
        
        # Lists Analysis
        st.write("### 📝 Lists")
        list_data = []
        for result in results:
            list_data.append({
                'URL': result['url'][:40] + '...' if len(result['url']) > 40 else result['url'],
                'Lists': result.get('lists_count', 0),
                'Avg Items/List': f"{result.get('avg_items_per_list', 0):.1f}",
                'List Coverage': f"{result.get('list_coverage_ratio', 0):.2f}",
                'Snippet Ready': '✅ High' if result.get('list_coverage_ratio', 0) > 0.3 else '⚠️ Low'
            })
        
        df_lists = pd.DataFrame(list_data)
        st.dataframe(df_lists, use_container_width=True)
    
    with tab4:
        st.subheader("🔗 URL Structure & Internal Linking")
        
        # URL Analysis
        url_data = []
        for result in results:
            url_data.append({
                'URL': result['url'][:50] + '...' if len(result['url']) > 50 else result['url'],
                'URL Depth': result.get('url_depth', 0),
                'Token Count': result.get('url_token_count', 0),
                'Keyword Match': f"{result.get('keyword_presence_ratio', 0):.2f}",
                'Stopword Ratio': f"{result.get('stopword_ratio', 0):.2f}",
                'Deep Link Density': f"{result.get('deep_link_density', 0):.2f}",
                'Subfolder': result.get('most_common_subfolder', 'Root')
            })
        
        df_urls = pd.DataFrame(url_data)
        st.dataframe(df_urls, use_container_width=True)
        
        # URL Quality Assessment
        st.write("### 🎯 URL Quality Assessment")
        for result in results:
            url = result['url']
            quality_score = 0
            issues = []
            
            # Check URL depth
            if result.get('url_depth', 0) >= 2:
                quality_score += 1
            else:
                issues.append("Consider using subfolders for better organization")
            
            # Check stopword ratio
            if result.get('stopword_ratio', 1) < 0.3:
                quality_score += 1
            else:
                issues.append("High stopword ratio - consider more semantic URLs")
            
            # Check token count
            if 3 <= result.get('url_token_count', 0) <= 6:
                quality_score += 1
            else:
                issues.append("URL should have 3-6 meaningful tokens")
            
            st.write(f"**{url[:60]}{'...' if len(url) > 60 else ''}**")
            st.write(f"Quality Score: {quality_score}/3 {'✅' if quality_score >= 2 else '⚠️'}")
            if issues:
                for issue in issues:
                    st.write(f"- ⚠️ {issue}")
            st.write("---")
    
    with tab5:
        st.subheader("⚡ Performance & Technical Analysis")
        
        # HTML vs JS Analysis
        st.write("### 🔧 HTML vs JavaScript Balance")
        tech_data = []
        for result in results:
            html_ratio = result.get('html_js_byte_ratio', 1)
            tech_data.append({
                'URL': result['url'][:40] + '...' if len(result['url']) > 40 else result['url'],
                'HTML/JS Ratio': f"{html_ratio:.2f}",
                'Script Density': f"{result.get('script_tag_density', 0):.3f}",
                'External JS': result.get('external_js_count', 0),
                'Inline JS Size': f"{result.get('inline_js_size', 0)/1024:.1f} KB",
                'AEO Friendly': '✅ Good' if html_ratio > 0.7 else '⚠️ JS Heavy'
            })
        
        df_tech = pd.DataFrame(tech_data)
        st.dataframe(df_tech, use_container_width=True)
        
        # Performance Insights
        st.write("### 🚀 Performance Recommendations")
        for result in results:
            if result['performance_insights']:
                st.write(f"**{result['url'][:60]}{'...' if len(result['url']) > 60 else ''}:**")
                for insight in result['performance_insights']:
                    st.write(f"⚠️ {insight}")
                st.write("---")
            else:
                st.write(f"**{result['url'][:60]}{'...' if len(result['url']) > 60 else ''}:** ✅ No major performance issues detected")
                st.write("---")
    
    with tab6:
        st.subheader("📱 Frameworks & Structured Data")
        
        # Framework Detection
        st.write("### 🛠️ Framework Detection")
        all_frameworks = {}
        for result in results:
            for framework in result['frameworks_detected']:
                if framework not in all_frameworks:
                    all_frameworks[framework] = []
                all_frameworks[framework].append(result['url'])
        
        if all_frameworks:
            for framework, urls in all_frameworks.items():
                st.write(f"**{framework}:**")
                for url in urls:
                    st.write(f"- {url[:60]}{'...' if len(url) > 60 else ''}")
                st.write("---")
        else:
            st.write("No popular frameworks detected in the analyzed URLs.")
        
        # Schema Markup Analysis
        st.write("### 📊 Schema.org Structured Data")
        schema_data = []
        for result in results:
            schema_types_str = ', '.join(result.get('schema_types', [])) if result.get('schema_types') else 'None'
            schema_data.append({
                'URL': result['url'][:40] + '...' if len(result['url']) > 40 else result['url'],
                'JSON-LD Blocks': result.get('jsonld_blocks_count', 0),
                'Schema Types': schema_types_str,
                'AEO Ready': '✅ Yes' if result.get('schema_blocks_count', 0) > 0 else '❌ Missing'
            })
        
        df_schema = pd.DataFrame(schema_data)
        st.dataframe(df_schema, use_container_width=True)
        
        # Schema recommendations
        missing_schema = [r for r in results if r.get('schema_blocks_count', 0) == 0]
        if missing_schema:
            st.write("### 🎯 Schema Recommendations")
            st.write("Consider adding structured data to these pages:")
            for result in missing_schema:
                st.write(f"- {result['url']}")
                st.write("  Recommended: Article, FAQPage, or BreadcrumbList schema")
            st.write("Structured data helps answer engines understand and feature your content.")

if __name__ == "__main__":
    main() 