"""
Legacy Django model file for testing PyRustor.

This file contains common patterns found in older Django codebases
that need modernization.
"""

import django
from django.db import models
from django.contrib.auth.models import User
import ConfigParser
import urllib2
from imp import reload

class UserProfile(models.Model):
    """User profile model with legacy patterns."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def get_display_name(self):
        """Get user display name using old string formatting."""
        if self.location:
            return "User: %s (%s)" % (self.user.username, self.location)
        else:
            return "User: %s" % self.user.username
    
    def load_config(self):
        """Load configuration using deprecated ConfigParser."""
        config = ConfigParser.ConfigParser()
        config.read('user_settings.ini')
        return config
    
    def fetch_external_data(self, url):
        """Fetch external data using urllib2."""
        try:
            response = urllib2.urlopen(url)
            return response.read()
        except Exception as e:
            return "Error: %s" % str(e)
    
    def format_profile_summary(self):
        """Format profile summary using old string formatting."""
        age = self.calculate_age()
        return "Profile: %s, Age: %d, Location: %s" % (
            self.user.username, 
            age if age else 0, 
            self.location or "Unknown"
        )
    
    def calculate_age(self):
        """Calculate user age."""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year
        return None

class OldStyleManager(models.Manager):
    """Manager with old-style patterns."""
    
    def get_active_users(self):
        """Get active users using old patterns."""
        return self.filter(is_active=True)
    
    def get_users_by_location(self, location):
        """Get users by location with old string formatting."""
        users = self.filter(location=location)
        return "Found %d users in %s" % (users.count(), location)

class BlogPost(models.Model):
    """Blog post model with legacy patterns."""
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=500, blank=True)
    
    objects = OldStyleManager()
    
    def __str__(self):
        """String representation using old formatting."""
        return "Post: %s by %s" % (self.title, self.author.user.username)
    
    def get_summary(self):
        """Get post summary with old string formatting."""
        word_count = len(self.content.split())
        return "Title: %s, Words: %d, Author: %s" % (
            self.title, 
            word_count, 
            self.author.user.username
        )
    
    def reload_config(self):
        """Reload configuration using deprecated imp module."""
        import sys
        if 'blog_config' in sys.modules:
            reload(sys.modules['blog_config'])

class Comment(models.Model):
    """Comment model with legacy patterns."""
    
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return "Comment by %s on %s" % (self.author.username, self.post.title)
    
    def get_status_message(self):
        """Get status message using old formatting."""
        status = "approved" if self.is_approved else "pending"
        return "Comment status: %s for post '%s'" % (status, self.post.title)

def old_helper_function(posts):
    """Legacy helper function for processing posts."""
    result = []
    for post in posts:
        if post is not None:
            summary = "Post: %s (%d words)" % (
                post.title, 
                len(post.content.split())
            )
            result.append(summary)
    return result

def fetch_post_data(post_id):
    """Fetch post data using legacy patterns."""
    try:
        post = BlogPost.objects.get(id=post_id)
        return "Found post: %s" % post.title
    except BlogPost.DoesNotExist:
        return "Post not found: ID %d" % post_id

def generate_report(start_date, end_date):
    """Generate report using old string formatting."""
    posts = BlogPost.objects.filter(
        created_at__range=[start_date, end_date]
    )
    
    total_posts = posts.count()
    total_comments = Comment.objects.filter(
        post__in=posts
    ).count()
    
    return "Report: %d posts, %d comments between %s and %s" % (
        total_posts,
        total_comments,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
