"""
Legacy data science script for testing PyRustor.

This file contains common patterns found in older data science codebases
that need modernization.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from imp import reload
import ConfigParser
import urllib2
import cPickle as pickle
import Queue as queue
from collections import OrderedDict

class DataAnalyzer:
    """Data analyzer with legacy patterns."""
    
    def __init__(self, config_path):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_path)
        self.data = None
        self.results_queue = queue.Queue()
        self.cache = OrderedDict()
    
    def load_data_from_url(self, url):
        """Load data from URL using urllib2."""
        try:
            response = urllib2.urlopen(url)
            data = response.read()
            
            # Save to temporary file and load with pandas
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write(data)
                temp_file = f.name
            
            self.data = pd.read_csv(temp_file)
            return "Loaded %d rows from %s" % (len(self.data), url)
            
        except Exception as e:
            return "Error loading data: %s" % str(e)
    
    def load_data_from_file(self, file_path):
        """Load data from file with legacy error handling."""
        try:
            self.data = pd.read_csv(file_path)
            return "Successfully loaded %d rows from %s" % (
                len(self.data), 
                file_path
            )
        except Exception as e:
            return "Failed to load data: %s" % str(e)
    
    def generate_report(self, title, data_summary):
        """Generate report using old string formatting."""
        if data_summary is None or len(data_summary) == 0:
            return "No data available for report: %s" % title
        
        header = "=== Report: %s ===" % title
        stats = "Data points: %d, Mean: %.2f, Std: %.2f" % (
            len(data_summary), 
            data_summary.mean(), 
            data_summary.std()
        )
        
        return "%s\n%s" % (header, stats)
    
    def plot_data(self, x_col, y_col, title=None):
        """Plot data with legacy patterns."""
        if self.data is None:
            return "No data loaded for plotting"
        
        if x_col not in self.data.columns or y_col not in self.data.columns:
            return "Columns not found: %s, %s" % (x_col, y_col)
        
        plt.figure(figsize=(10, 6))
        plt.plot(self.data[x_col], self.data[y_col])
        
        plot_title = title or "Plot: %s vs %s" % (x_col, y_col)
        plt.title(plot_title)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        
        return "Plot created: %s" % plot_title
    
    def save_results(self, results, filename):
        """Save results using cPickle."""
        try:
            with open(filename, 'wb') as f:
                pickle.dump(results, f)
            return "Results saved to %s" % filename
        except Exception as e:
            return "Error saving results: %s" % str(e)
    
    def load_results(self, filename):
        """Load results using cPickle."""
        try:
            with open(filename, 'rb') as f:
                results = pickle.load(f)
            return results
        except Exception as e:
            return "Error loading results: %s" % str(e)
    
    def cache_result(self, key, value):
        """Cache result using OrderedDict."""
        self.cache[key] = value
        
        # Keep cache size limited
        if len(self.cache) > 100:
            self.cache.popitem(last=False)
        
        return "Cached result for key: %s" % key

def process_dataset(file_path, output_format="csv"):
    """Process dataset with legacy patterns."""
    analyzer = DataAnalyzer("analysis_config.ini")
    
    # Load and process data
    load_result = analyzer.load_data_from_file(file_path)
    print("Load result: %s" % load_result)
    
    if analyzer.data is None:
        return "Failed to process dataset: %s" % file_path
    
    # Generate summary statistics
    numeric_columns = analyzer.data.select_dtypes(include=[np.number]).columns
    summary_stats = {}
    
    for col in numeric_columns:
        stats = {
            'mean': analyzer.data[col].mean(),
            'std': analyzer.data[col].std(),
            'min': analyzer.data[col].min(),
            'max': analyzer.data[col].max()
        }
        summary_stats[col] = stats
    
    # Format summary
    summary_text = "Dataset shape: %s, Columns: %s" % (
        str(analyzer.data.shape), 
        ", ".join(analyzer.data.columns)
    )
    
    return summary_text, summary_stats

def old_statistical_function(values):
    """Old statistical function with legacy patterns."""
    if len(values) == 0:
        return "No data provided: %s" % str(values)
    
    # Calculate basic statistics
    mean_val = sum(values) / len(values)
    variance = sum((x - mean_val) ** 2 for x in values) / len(values)
    std_dev = variance ** 0.5
    
    return "Statistics - Mean: %.2f, Std: %.2f, Count: %d" % (
        mean_val, 
        std_dev, 
        len(values)
    )

def correlation_analysis(data, col1, col2):
    """Perform correlation analysis with legacy formatting."""
    if col1 not in data.columns or col2 not in data.columns:
        return "Columns not found: %s, %s" % (col1, col2)
    
    correlation = data[col1].corr(data[col2])
    
    if abs(correlation) > 0.7:
        strength = "strong"
    elif abs(correlation) > 0.3:
        strength = "moderate"
    else:
        strength = "weak"
    
    return "Correlation between %s and %s: %.3f (%s)" % (
        col1, col2, correlation, strength
    )

def batch_process_files(file_list, output_dir):
    """Batch process multiple files with legacy patterns."""
    results = []
    
    for i, file_path in enumerate(file_list):
        try:
            summary, stats = process_dataset(file_path)
            
            result_info = "File %d/%d: %s - %s" % (
                i + 1, 
                len(file_list), 
                file_path, 
                summary
            )
            
            results.append(result_info)
            
        except Exception as e:
            error_info = "Error processing file %s: %s" % (file_path, str(e))
            results.append(error_info)
    
    return results

def generate_visualization_report(data, output_path):
    """Generate visualization report with legacy patterns."""
    if data is None or len(data) == 0:
        return "No data available for visualization"
    
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) < 2:
        return "Insufficient numeric columns for visualization: %d" % len(numeric_cols)
    
    # Create multiple plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Histogram
    axes[0, 0].hist(data[numeric_cols[0]], bins=20)
    axes[0, 0].set_title("Histogram: %s" % numeric_cols[0])
    
    # Scatter plot
    if len(numeric_cols) >= 2:
        axes[0, 1].scatter(data[numeric_cols[0]], data[numeric_cols[1]])
        axes[0, 1].set_title("Scatter: %s vs %s" % (numeric_cols[0], numeric_cols[1]))
    
    # Box plot
    axes[1, 0].boxplot(data[numeric_cols[0]].dropna())
    axes[1, 0].set_title("Box plot: %s" % numeric_cols[0])
    
    # Line plot
    axes[1, 1].plot(data[numeric_cols[0]].values)
    axes[1, 1].set_title("Line plot: %s" % numeric_cols[0])
    
    plt.tight_layout()
    plt.savefig(output_path)
    
    return "Visualization saved to: %s" % output_path

# Main analysis workflow
if __name__ == "__main__":
    print("Starting data analysis workflow...")
    
    # Initialize analyzer
    analyzer = DataAnalyzer("analysis_config.ini")
    
    # Process sample data
    sample_files = ["data1.csv", "data2.csv", "data3.csv"]
    results = batch_process_files(sample_files, "output/")
    
    for result in results:
        print("Result: %s" % result)
    
    print("Analysis workflow completed.")
