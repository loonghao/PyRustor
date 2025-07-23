"""
Legacy Flask application for testing PyRustor.

This file contains common patterns found in older Flask applications
that need modernization.
"""

from flask import Flask, request, jsonify, render_template, session
import urllib2
import urlparse
from imp import reload
import ConfigParser
import cPickle as pickle
import Queue as queue
from HTMLParser import HTMLParser

app = Flask(__name__)
app.secret_key = 'legacy_secret_key'

class DatabaseManager:
    """Database manager with legacy patterns."""
    
    def __init__(self, config_file):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        self.connection_pool = queue.Queue()
    
    def fetch_data(self, url):
        """Fetch data using urllib2."""
        try:
            response = urllib2.urlopen(url)
            return response.read()
        except Exception as e:
            return "Error fetching data: %s" % str(e)
    
    def format_response(self, data, status):
        """Format response using old string formatting."""
        return "Status: %d, Data: %s" % (status, data)
    
    def serialize_data(self, data):
        """Serialize data using cPickle."""
        return pickle.dumps(data)
    
    def deserialize_data(self, serialized_data):
        """Deserialize data using cPickle."""
        return pickle.loads(serialized_data)
    
    def parse_url(self, url):
        """Parse URL using urlparse."""
        parsed = urlparse.urlparse(url)
        return "Scheme: %s, Host: %s, Path: %s" % (
            parsed.scheme, 
            parsed.netloc, 
            parsed.path
        )

class LegacyHTMLParser(HTMLParser):
    """Legacy HTML parser using old HTMLParser."""
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
        self.text_content = []
    
    def handle_starttag(self, tag, attrs):
        """Handle start tag."""
        if tag == 'a':
            for attr_name, attr_value in attrs:
                if attr_name == 'href':
                    self.links.append(attr_value)
    
    def handle_data(self, data):
        """Handle text data."""
        self.text_content.append(data.strip())
    
    def get_summary(self):
        """Get parsing summary."""
        return "Found %d links and %d text blocks" % (
            len(self.links), 
            len(self.text_content)
        )

# Global database manager instance
db_manager = DatabaseManager('config.ini')

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """Get user endpoint with legacy patterns."""
    try:
        user_data = db_manager.fetch_data(
            "http://api.example.com/users/%d" % user_id
        )
        
        if user_data:
            response_data = {
                "user_id": user_id,
                "data": user_data,
                "message": "User found: ID %d" % user_id
            }
            return jsonify(response_data)
        else:
            return jsonify({
                "error": "User not found: ID %d" % user_id
            }), 404
            
    except Exception as e:
        error_msg = "Error retrieving user %d: %s" % (user_id, str(e))
        return jsonify({"error": error_msg}), 500

@app.route('/api/search')
def search_users():
    """Search users with legacy patterns."""
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    
    if not query:
        return jsonify({
            "error": "Query parameter 'q' is required"
        }), 400
    
    try:
        search_url = "http://api.example.com/search?q=%s&page=%d" % (
            query, page
        )
        
        search_results = db_manager.fetch_data(search_url)
        
        return jsonify({
            "query": query,
            "page": page,
            "results": search_results,
            "message": "Search completed for: %s" % query
        })
        
    except Exception as e:
        return jsonify({
            "error": "Search failed: %s" % str(e)
        }), 500

@app.route('/api/parse_html', methods=['POST'])
def parse_html():
    """Parse HTML content using legacy parser."""
    html_content = request.json.get('html', '')
    
    if not html_content:
        return jsonify({
            "error": "HTML content is required"
        }), 400
    
    try:
        parser = LegacyHTMLParser()
        parser.feed(html_content)
        
        return jsonify({
            "links": parser.links,
            "text_blocks": parser.text_content,
            "summary": parser.get_summary()
        })
        
    except Exception as e:
        return jsonify({
            "error": "HTML parsing failed: %s" % str(e)
        }), 500

@app.route('/admin/reload_config')
def reload_config():
    """Reload configuration using deprecated imp module."""
    try:
        import sys
        if 'app_config' in sys.modules:
            reload(sys.modules['app_config'])
        
        return jsonify({
            "message": "Configuration reloaded successfully"
        })
        
    except Exception as e:
        return jsonify({
            "error": "Config reload failed: %s" % str(e)
        }), 500

def legacy_helper_function(items):
    """Legacy helper function."""
    result = []
    for item in items:
        if item is not None:
            formatted_item = "Item: %s (Type: %s)" % (
                str(item), 
                type(item).__name__
            )
            result.append(formatted_item)
    return result

def validate_url(url):
    """Validate URL using legacy urlparse."""
    try:
        parsed = urlparse.urlparse(url)
        if parsed.scheme and parsed.netloc:
            return "Valid URL: %s" % url
        else:
            return "Invalid URL: %s" % url
    except Exception as e:
        return "URL validation error: %s" % str(e)

def process_queue_data():
    """Process data from queue using legacy Queue module."""
    data_queue = queue.Queue()
    
    # Add some sample data
    for i in range(5):
        data_queue.put("Item %d" % i)
    
    results = []
    while not data_queue.empty():
        item = data_queue.get()
        processed = "Processed: %s" % item
        results.append(processed)
    
    return results

def serialize_session_data(data):
    """Serialize session data using cPickle."""
    try:
        serialized = pickle.dumps(data)
        return "Serialized %d bytes of data" % len(serialized)
    except Exception as e:
        return "Serialization error: %s" % str(e)

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors with legacy formatting."""
    return jsonify({
        "error": "Not found: %s" % request.url,
        "status": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with legacy formatting."""
    return jsonify({
        "error": "Internal server error: %s" % str(error),
        "status": 500
    }), 500

if __name__ == '__main__':
    # Legacy application startup
    print("Starting Flask application...")
    print("Database manager initialized with config: %s" % db_manager.config)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
