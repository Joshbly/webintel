# WebIntel - AEO HTML Analysis Tool

A powerful Streamlit application that analyzes website HTML structure with a focus on **Answer Engine Optimization (AEO)** best practices. Perfect for SEO specialists, content creators, and digital marketers who want to optimize their content for AI-powered answer engines like ChatGPT, Claude, Perplexity, and Google's AI overviews.

## Features

### 🎯 Answer Engine Optimization (AEO) Analysis
- **Atomic Paragraphs**: Analyze paragraph length and structure for snippet optimization
- **2025 Freshness Signals**: Check for current year inclusion in URLs, titles, meta descriptions, and content
- **Schema Markup Detection**: Identify and validate JSON-LD structured data
- **HTML vs JavaScript Balance**: Ensure content is server-side rendered for answer engines
- **Table & List Analysis**: Optimize data presentation for featured snippets
- **Semantic URL Structure**: Evaluate URL token quality and keyword presence
- **Heading Coverage**: Assess H2/H3 structure for content organization

### 🔧 Technical Analysis
- **Bulk URL Processing**: Analyze multiple URLs simultaneously
- **Anti-Blocking Technology**: Uses multiple HTTP libraries with realistic browser headers
- **Framework Detection**: Identify React, Vue, Angular, WordPress, and more
- **Performance Insights**: Get actionable optimization recommendations
- **Subfolder Analysis**: Evaluate site structure and internal linking
- **Complete HTML Metrics**: Tag analysis, resource counting, and accessibility checks

### 🚀 Team & Deployment Ready
- **Beautiful Interface**: Modern Streamlit UI with organized AEO-focused tabs
- **Easy Deployment**: Multiple options for team collaboration
- **Export Ready**: Comprehensive analysis in organized data tables

## Quick Start

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <your-repo>
   cd WebIntel
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   streamlit run app.py
   ```

3. **Access the App**
   Open your browser to `http://localhost:8501`

## Usage

1. **Enter URLs**: Add URLs one per line in the text area or upload a text file
2. **Configure Settings**: Adjust timeout and max URLs in the sidebar
3. **Analyze**: Click "🚀 Analyze URLs" to start processing
4. **Explore AEO Results**: Navigate through comprehensive analysis tabs:
   - **🏗️ Structure Overview**: High-level comparison of all URLs
   - **🎯 AEO Analysis**: Atomic paragraphs, freshness signals, and content structure
   - **📊 Tables & Lists**: Data presentation optimization for snippets
   - **🔗 URLs & Links**: Semantic URL structure and internal linking
   - **⚡ Performance**: HTML vs JS balance and technical recommendations
   - **📱 Frameworks & Schema**: Technology detection and structured data analysis

## Deployment Options

### Option 1: Streamlit Cloud (Recommended for Teams)

1. **Push to GitHub**: Commit your code to a GitHub repository
2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select `app.py` as the main file
   - Deploy automatically

**Pros**: Free, automatic updates, easy sharing, no server maintenance
**Cons**: Public unless you have Streamlit Cloud for Teams

### Option 2: Heroku

1. **Create Heroku App**
   ```bash
   # Install Heroku CLI first
   heroku create your-webintel-app
   ```

2. **Add Procfile**
   ```bash
   echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
   ```

3. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy WebIntel"
   git push heroku main
   ```

**Pros**: Custom domain, more control, can handle higher traffic
**Cons**: Costs money after free tier, requires more setup

### Option 3: Docker + Cloud Provider

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
   
   ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Deploy to Cloud Provider** (AWS, GCP, Azure, DigitalOcean, etc.)

**Pros**: Most flexible, scalable, can add custom features
**Cons**: Requires Docker knowledge, more complex setup

### Option 4: Company Server

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run with Custom Settings**
   ```bash
   streamlit run app.py --server.port=8080 --server.address=0.0.0.0
   ```

3. **Access via Internal Network**
   Share the server IP and port with your team

**Pros**: Full control, keeps data internal, no external dependencies
**Cons**: Requires server maintenance, IT support needed

## Advanced Features

### Custom Headers and Anti-Blocking

The app includes several anti-blocking measures:
- Realistic browser User-Agent headers
- Proper Accept headers
- Connection keep-alive
- Automatic redirects
- Fallback to multiple HTTP libraries

### Framework Detection

Automatically detects popular frameworks:
- **Frontend**: React, Vue.js, Angular, jQuery
- **CSS**: Bootstrap, Tailwind CSS
- **CMS**: WordPress
- **And more...**

### Performance Insights

Provides actionable recommendations:
- Bundle optimization suggestions
- Image loading improvements
- HTML size optimization
- Accessibility improvements

## Configuration

### Environment Variables

You can customize behavior with environment variables:

```bash
# Maximum processing time per URL (seconds)
export WEBINTEL_TIMEOUT=30

# Maximum URLs to process in one batch
export WEBINTEL_MAX_URLS=20

# Custom User-Agent string
export WEBINTEL_USER_AGENT="Your Custom Bot"
```

### Streamlit Configuration

Create `.streamlit/config.toml` for custom settings:

```toml
[server]
port = 8501
address = "0.0.0.0"

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[browser]
gatherUsageStats = false
```

## Troubleshooting

### Common Issues

1. **URLs not loading**
   - Check if URLs are accessible from your network
   - Some sites block automated requests
   - Try adding custom headers or using a VPN

2. **Slow performance**
   - Reduce the number of URLs processed simultaneously
   - Increase timeout for slow websites
   - Consider processing in smaller batches

3. **Deployment issues**
   - Ensure all dependencies are in requirements.txt
   - Check that the deployment platform supports the Python version
   - Verify network access to external URLs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - feel free to use and modify for your needs.

## Support

For issues or feature requests, please create an issue in the GitHub repository. 