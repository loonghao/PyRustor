"""
Real-world file testing for PyRustor.

This module tests PyRustor with actual Python files that represent
common patterns found in real codebases.
"""

import pytest
import tempfile
import os
from pathlib import Path
import pyrustor


class TestRealWorldFiles:
    """Test PyRustor with real-world Python file patterns."""

    def test_django_model_file(self, temp_directory):
        """Test parsing and refactoring a Django model file."""
        django_model = '''
import django
from django.db import models
from django.contrib.auth.models import User
import ConfigParser

class UserProfile(models.Model):
    """User profile model with legacy patterns."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    def get_display_name(self):
        """Get user display name using old string formatting."""
        return "User: %s (%s)" % (self.user.username, self.location)
    
    def load_config(self):
        """Load configuration using deprecated ConfigParser."""
        config = ConfigParser.ConfigParser()
        return config

class OldStyleManager(models.Manager):
    """Manager with old-style patterns."""
    
    def get_active_users(self):
        return self.filter(is_active=True)

class BlogPost(models.Model):
    """Blog post model."""
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = OldStyleManager()
    
    def __str__(self):
        return "Post: %s by %s" % (self.title, self.author.user.username)
'''
        
        # Write to temporary file
        test_file = temp_directory / "django_models.py"
        test_file.write_text(django_model)
        
        # Test parsing
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(test_file))
        
        assert not ast.is_empty()
        assert ast.statement_count() > 0
        
        # Test class detection
        classes = ast.class_names()
        assert "UserProfile" in classes
        assert "BlogPost" in classes
        assert "OldStyleManager" in classes
        
        # Test function detection
        functions = ast.function_names()
        assert "get_display_name" in functions
        assert "load_config" in functions
        
        # Test refactoring
        refactor = pyrustor.Refactor(ast)
        
        # Modernize imports
        refactor.replace_import("ConfigParser", "configparser")
        
        # Rename classes
        refactor.rename_class("OldStyleManager", "ModernManager")
        
        # Modernize syntax
        refactor.modernize_syntax()
        
        # Get result
        result = refactor.get_code()
        
        # Verify changes
        assert "configparser" in result
        assert "ModernManager" in result
        assert "ConfigParser" not in result or "import configparser" in result

    def test_flask_app_file(self, temp_directory):
        """Test parsing and refactoring a Flask application file."""
        flask_app = '''
from flask import Flask, request, jsonify
import urllib2
from imp import reload
import ConfigParser

app = Flask(__name__)

class DatabaseManager:
    """Database manager with legacy patterns."""
    
    def __init__(self, config_file):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
    
    def fetch_data(self, url):
        """Fetch data using urllib2."""
        response = urllib2.urlopen(url)
        return response.read()
    
    def format_response(self, data, status):
        """Format response using old string formatting."""
        return "Status: %d, Data: %s" % (status, data)

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """Get user endpoint with legacy patterns."""
    db = DatabaseManager('config.ini')
    
    try:
        user_data = db.fetch_data("http://api.example.com/users/%d" % user_id)
        return jsonify({"user": user_data})
    except Exception as e:
        return jsonify({"error": "Error: %s" % str(e)}), 500

def legacy_helper_function(items):
    """Legacy helper function."""
    result = []
    for item in items:
        if item is not None:
            result.append("Item: %s" % item)
    return result

if __name__ == '__main__':
    app.run(debug=True)
'''
        
        # Write to temporary file
        test_file = temp_directory / "flask_app.py"
        test_file.write_text(flask_app)
        
        # Test parsing
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(test_file))
        
        assert not ast.is_empty()
        
        # Test imports detection
        imports = ast.imports()
        assert len(imports) > 0
        
        # Test refactoring
        refactor = pyrustor.Refactor(ast)
        
        # Modernize imports
        refactor.replace_import("urllib2", "urllib.request")
        refactor.replace_import("ConfigParser", "configparser")
        refactor.replace_import("imp", "importlib")
        
        # Rename functions
        refactor.rename_function("legacy_helper_function", "modern_helper_function")
        
        # Modernize syntax
        refactor.modernize_syntax()
        
        # Get result
        result = refactor.get_code()
        
        # Verify changes
        assert "urllib.request" in result or "urllib2" not in result
        assert "configparser" in result or "ConfigParser" not in result
        assert "modern_helper_function" in result

    def test_data_science_notebook_file(self, temp_directory):
        """Test parsing a data science script with common patterns."""
        data_science_script = '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from imp import reload
import ConfigParser
import urllib2

class DataAnalyzer:
    """Data analyzer with legacy patterns."""
    
    def __init__(self, config_path):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_path)
        self.data = None
    
    def load_data_from_url(self, url):
        """Load data from URL using urllib2."""
        response = urllib2.urlopen(url)
        data = response.read()
        return pd.read_csv(data)
    
    def generate_report(self, title, data_summary):
        """Generate report using old string formatting."""
        header = "Report: %s" % title
        summary = "Data points: %d, Mean: %.2f" % (len(data_summary), data_summary.mean())
        return "%s\\n%s" % (header, summary)
    
    def plot_data(self, x_col, y_col):
        """Plot data with legacy patterns."""
        if self.data is not None:
            plt.figure(figsize=(10, 6))
            plt.plot(self.data[x_col], self.data[y_col])
            plt.title("Plot: %s vs %s" % (x_col, y_col))
            plt.show()

def process_dataset(file_path, output_format="csv"):
    """Process dataset with legacy patterns."""
    analyzer = DataAnalyzer("config.ini")
    
    # Load and process data
    data = pd.read_csv(file_path)
    
    # Generate summary
    summary = "Dataset shape: %s, Columns: %s" % (str(data.shape), ", ".join(data.columns))
    
    return summary

def old_statistical_function(values):
    """Old statistical function."""
    if len(values) == 0:
        return "No data: %s" % str(values)
    
    mean_val = sum(values) / len(values)
    return "Mean: %.2f" % mean_val

# Main analysis
if __name__ == "__main__":
    analyzer = DataAnalyzer("analysis_config.ini")
    result = process_dataset("data.csv")
    print("Analysis result: %s" % result)
'''
        
        # Write to temporary file
        test_file = temp_directory / "data_analysis.py"
        test_file.write_text(data_science_script)
        
        # Test parsing
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(test_file))
        
        assert not ast.is_empty()
        
        # Test class and function detection
        classes = ast.class_names()
        functions = ast.function_names()
        
        assert "DataAnalyzer" in classes
        assert "process_dataset" in functions
        assert "old_statistical_function" in functions
        
        # Test refactoring
        refactor = pyrustor.Refactor(ast)
        
        # Modernize imports
        refactor.replace_import("ConfigParser", "configparser")
        refactor.replace_import("urllib2", "urllib.request")
        refactor.replace_import("imp", "importlib")
        
        # Rename functions
        refactor.rename_function("old_statistical_function", "modern_statistical_function")
        
        # Modernize syntax
        refactor.modernize_syntax()
        
        # Get result and verify
        result = refactor.get_code()
        assert "modern_statistical_function" in result

    def test_legacy_web_scraper_file(self, temp_directory):
        """Test parsing a legacy web scraper file."""
        web_scraper = '''
import urllib2
import urlparse
from HTMLParser import HTMLParser
import ConfigParser
from imp import reload
import cookielib

class LegacyWebScraper(HTMLParser):
    """Legacy web scraper using old libraries."""
    
    def __init__(self, config_file):
        HTMLParser.__init__(self)
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        self.links = []
        self.cookies = cookielib.CookieJar()
    
    def fetch_page(self, url):
        """Fetch page using urllib2."""
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
        response = opener.open(url)
        return response.read()
    
    def parse_url(self, url):
        """Parse URL using urlparse."""
        parsed = urlparse.urlparse(url)
        return "Scheme: %s, Host: %s, Path: %s" % (parsed.scheme, parsed.netloc, parsed.path)
    
    def handle_starttag(self, tag, attrs):
        """Handle start tag."""
        if tag == 'a':
            for attr_name, attr_value in attrs:
                if attr_name == 'href':
                    self.links.append(attr_value)
    
    def get_links_summary(self):
        """Get summary of found links."""
        return "Found %d links: %s" % (len(self.links), ", ".join(self.links[:5]))

def scrape_website(url, config_path):
    """Scrape website using legacy methods."""
    scraper = LegacyWebScraper(config_path)
    
    try:
        content = scraper.fetch_page(url)
        scraper.feed(content)
        return scraper.get_links_summary()
    except Exception as e:
        return "Error scraping %s: %s" % (url, str(e))

def old_url_validator(url):
    """Validate URL using old methods."""
    parsed = urlparse.urlparse(url)
    if parsed.scheme and parsed.netloc:
        return "Valid URL: %s" % url
    else:
        return "Invalid URL: %s" % url
'''
        
        # Write to temporary file
        test_file = temp_directory / "web_scraper.py"
        test_file.write_text(web_scraper)
        
        # Test parsing
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(test_file))
        
        assert not ast.is_empty()
        
        # Test refactoring
        refactor = pyrustor.Refactor(ast)
        
        # Modernize imports
        refactor.replace_import("urllib2", "urllib.request")
        refactor.replace_import("urlparse", "urllib.parse")
        refactor.replace_import("HTMLParser", "html.parser")
        refactor.replace_import("ConfigParser", "configparser")
        refactor.replace_import("cookielib", "http.cookiejar")
        
        # Rename functions
        refactor.rename_function("old_url_validator", "modern_url_validator")
        
        # Modernize syntax
        refactor.modernize_syntax()
        
        # Get result
        result = refactor.get_code()
        
        # Verify some changes
        assert "modern_url_validator" in result
