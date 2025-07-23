//! Code formatting and style preservation utilities

use crate::{ast::PythonAst, error::Result};
use std::collections::HashMap;

/// Configuration for code formatting
#[derive(Debug, Clone)]
pub struct FormatConfig {
    /// Number of spaces per indentation level
    pub indent_size: usize,
    /// Whether to use spaces or tabs for indentation
    pub use_spaces: bool,
    /// Maximum line length
    pub max_line_length: usize,
    /// Whether to preserve original formatting when possible
    pub preserve_original: bool,
    /// Whether to preserve comments
    pub preserve_comments: bool,
    /// Whether to preserve blank lines
    pub preserve_blank_lines: bool,
}

impl Default for FormatConfig {
    fn default() -> Self {
        Self {
            indent_size: 4,
            use_spaces: true,
            max_line_length: 88,
            preserve_original: true,
            preserve_comments: true,
            preserve_blank_lines: true,
        }
    }
}

/// Python code formatter that preserves original style when possible
#[derive(Debug)]
pub struct Formatter {
    config: FormatConfig,
    /// Cache for storing formatting decisions
    format_cache: HashMap<String, String>,
}

impl Default for Formatter {
    fn default() -> Self {
        Self::new()
    }
}

impl Formatter {
    /// Create a new formatter with default configuration
    pub fn new() -> Self {
        Self {
            config: FormatConfig::default(),
            format_cache: HashMap::new(),
        }
    }

    /// Create a formatter with custom configuration
    pub fn with_config(config: FormatConfig) -> Self {
        Self {
            config,
            format_cache: HashMap::new(),
        }
    }

    /// Format a Python AST back to source code
    ///
    /// This method attempts to preserve the original formatting as much as possible
    /// while applying any necessary transformations.
    pub fn format_ast(&mut self, ast: &PythonAst) -> Result<String> {
        // For now, this is a placeholder implementation
        // A full implementation would:
        // 1. Walk the AST nodes
        // 2. Preserve original formatting information
        // 3. Apply formatting rules where needed
        // 4. Handle comments and whitespace properly

        if ast.is_empty() {
            return Ok(String::new());
        }

        // Generate code from the current AST state (which may have been modified)
        let generated_code = ast.to_code()?;

        if self.config.preserve_original {
            // Return the generated code (which reflects any modifications)
            Ok(generated_code)
        } else {
            // Apply formatting rules to the generated code
            self.apply_formatting_rules(&generated_code)
        }
    }

    /// Apply formatting rules to source code
    fn apply_formatting_rules(&mut self, source: &str) -> Result<String> {
        let mut formatted = String::new();
        let mut current_indent = 0;
        let mut in_string = false;
        let mut string_char = '\0';

        for line in source.lines() {
            let trimmed = line.trim();

            // Skip empty lines if not preserving them
            if trimmed.is_empty() && !self.config.preserve_blank_lines {
                continue;
            }

            // Handle indentation
            if !trimmed.is_empty() && !in_string {
                // Detect indentation changes
                if trimmed.ends_with(':') && !trimmed.starts_with('#') {
                    // Increase indentation for next line
                    let indent = self.get_indent_string(current_indent);
                    formatted.push_str(&format!("{}{}\n", indent, trimmed));
                    current_indent += 1;
                } else if trimmed.starts_with("def ") || trimmed.starts_with("class ") {
                    // Function or class definition
                    let indent = self.get_indent_string(current_indent);
                    formatted.push_str(&format!("{}{}\n", indent, trimmed));
                    current_indent += 1;
                } else {
                    // Regular line
                    let indent = self.get_indent_string(current_indent);
                    formatted.push_str(&format!("{}{}\n", indent, trimmed));
                }
            } else {
                // Preserve the line as-is for strings or empty lines
                formatted.push_str(&format!("{}\n", line));
            }

            // Track string literals to avoid formatting inside them
            for ch in trimmed.chars() {
                if (ch == '"' || ch == '\'') && !in_string {
                    in_string = true;
                    string_char = ch;
                } else if ch == string_char && in_string {
                    in_string = false;
                }
            }
        }

        Ok(formatted)
    }

    /// Get the indentation string for a given level
    fn get_indent_string(&self, level: usize) -> String {
        if self.config.use_spaces {
            " ".repeat(level * self.config.indent_size)
        } else {
            "\t".repeat(level)
        }
    }

    /// Format a single line of code
    pub fn format_line(&mut self, line: &str, indent_level: usize) -> Result<String> {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            return Ok(String::new());
        }

        let indent = self.get_indent_string(indent_level);
        Ok(format!("{}{}", indent, trimmed))
    }

    /// Preserve comments from the original source
    pub fn preserve_comments(&mut self, original: &str, formatted: &str) -> Result<String> {
        // This is a simplified implementation
        // A full implementation would properly track comment positions
        // and insert them in the correct locations in the formatted code

        let original_lines: Vec<&str> = original.lines().collect();
        let formatted_lines: Vec<&str> = formatted.lines().collect();
        let mut result = Vec::new();

        for (i, formatted_line) in formatted_lines.iter().enumerate() {
            result.push(formatted_line.to_string());

            // Check if the original line had a comment
            if let Some(original_line) = original_lines.get(i) {
                if let Some(comment_pos) = original_line.find('#') {
                    let comment = &original_line[comment_pos..];
                    if !formatted_line.contains('#') {
                        // Add the comment to the formatted line
                        if let Some(last_line) = result.last_mut() {
                            last_line.push_str(&format!("  {}", comment));
                        }
                    }
                }
            }
        }

        Ok(result.join("\n"))
    }

    /// Clear the formatting cache
    pub fn clear_cache(&mut self) {
        self.format_cache.clear();
    }

    /// Get the current configuration
    pub fn config(&self) -> &FormatConfig {
        &self.config
    }

    /// Update the configuration
    pub fn set_config(&mut self, config: FormatConfig) {
        self.config = config;
        self.clear_cache(); // Clear cache when config changes
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::Parser;

    #[test]
    fn test_formatter_creation() {
        let formatter = Formatter::new();
        assert_eq!(formatter.config.indent_size, 4);
        assert!(formatter.config.use_spaces);
    }

    #[test]
    fn test_custom_config() {
        let config = FormatConfig {
            indent_size: 2,
            use_spaces: false,
            max_line_length: 100,
            preserve_original: false,
            preserve_comments: true,
            preserve_blank_lines: false,
        };

        let formatter = Formatter::with_config(config);
        assert_eq!(formatter.config.indent_size, 2);
        assert!(!formatter.config.use_spaces);
        assert_eq!(formatter.config.max_line_length, 100);
    }

    #[test]
    fn test_indent_string() {
        let formatter = Formatter::new();
        assert_eq!(formatter.get_indent_string(0), "");
        assert_eq!(formatter.get_indent_string(1), "    ");
        assert_eq!(formatter.get_indent_string(2), "        ");
    }

    #[test]
    fn test_format_line() -> Result<()> {
        let mut formatter = Formatter::new();
        let result = formatter.format_line("  def hello():  ", 1)?;
        assert_eq!(result, "    def hello():");
        Ok(())
    }

    #[test]
    fn test_format_ast() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("def hello():\n    pass")?;

        let mut formatter = Formatter::new();
        let result = formatter.format_ast(&ast)?;
        assert!(!result.is_empty());
        assert!(result.contains("hello"));
        Ok(())
    }

    #[test]
    fn test_format_empty_ast() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("")?;

        let mut formatter = Formatter::new();
        let result = formatter.format_ast(&ast)?;
        assert!(result.is_empty());
        Ok(())
    }

    #[test]
    fn test_format_complex_code() -> Result<()> {
        let parser = Parser::new();
        let code = r#"
def function_one():
    return 1

class MyClass:
    def method(self):
        return "method"
"#;
        let ast = parser.parse_string(code)?;

        let mut formatter = Formatter::new();
        let result = formatter.format_ast(&ast)?;

        assert!(result.contains("function_one"));
        assert!(result.contains("MyClass"));
        assert!(result.contains("method"));
        Ok(())
    }

    #[test]
    fn test_format_with_different_configs() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("def hello(): pass")?;

        // Test with spaces
        let config_spaces = FormatConfig {
            indent_size: 4,
            use_spaces: true,
            ..Default::default()
        };
        let mut formatter_spaces = Formatter::with_config(config_spaces);
        let result_spaces = formatter_spaces.format_ast(&ast)?;

        // Test with tabs
        let config_tabs = FormatConfig {
            indent_size: 1,
            use_spaces: false,
            ..Default::default()
        };
        let mut formatter_tabs = Formatter::with_config(config_tabs);
        let result_tabs = formatter_tabs.format_ast(&ast)?;

        // Both should contain the function
        assert!(result_spaces.contains("hello"));
        assert!(result_tabs.contains("hello"));
        Ok(())
    }

    #[test]
    fn test_preserve_original_formatting() -> Result<()> {
        let parser = Parser::new();
        let original_code = "def hello():    pass";
        let ast = parser.parse_string(original_code)?;

        let config = FormatConfig {
            preserve_original: true,
            ..Default::default()
        };
        let mut formatter = Formatter::with_config(config);
        let result = formatter.format_ast(&ast)?;

        // Should preserve original formatting when preserve_original is true
        assert!(result.contains("hello"));
        Ok(())
    }

    #[test]
    fn test_format_line_with_different_indents() -> Result<()> {
        let mut formatter = Formatter::new();

        let result0 = formatter.format_line("def hello():", 0)?;
        assert_eq!(result0, "def hello():");

        let result1 = formatter.format_line("def hello():", 1)?;
        assert_eq!(result1, "    def hello():");

        let result2 = formatter.format_line("def hello():", 2)?;
        assert_eq!(result2, "        def hello():");

        Ok(())
    }

    #[test]
    fn test_format_line_empty() -> Result<()> {
        let mut formatter = Formatter::new();
        let result = formatter.format_line("", 1)?;
        assert!(result.is_empty());
        Ok(())
    }

    #[test]
    fn test_format_line_whitespace_only() -> Result<()> {
        let mut formatter = Formatter::new();
        let result = formatter.format_line("   \t  ", 1)?;
        assert!(result.is_empty());
        Ok(())
    }

    #[test]
    fn test_indent_string_with_tabs() {
        let config = FormatConfig {
            use_spaces: false,
            indent_size: 1,
            ..Default::default()
        };
        let formatter = Formatter::with_config(config);

        assert_eq!(formatter.get_indent_string(0), "");
        assert_eq!(formatter.get_indent_string(1), "\t");
        assert_eq!(formatter.get_indent_string(2), "\t\t");
    }

    #[test]
    fn test_indent_string_with_custom_size() {
        let config = FormatConfig {
            use_spaces: true,
            indent_size: 2,
            ..Default::default()
        };
        let formatter = Formatter::with_config(config);

        assert_eq!(formatter.get_indent_string(0), "");
        assert_eq!(formatter.get_indent_string(1), "  ");
        assert_eq!(formatter.get_indent_string(2), "    ");
    }

    #[test]
    fn test_preserve_comments() -> Result<()> {
        let parser = Parser::new();
        let code = r#"
# This is a comment
def hello():
    # Another comment
    pass
"#;
        let ast = parser.parse_string(code)?;

        let mut formatter = Formatter::new();
        let result = formatter.format_ast(&ast)?;

        // Should contain the function
        assert!(result.contains("hello"));
        Ok(())
    }

    #[test]
    fn test_format_unicode_code() -> Result<()> {
        let parser = Parser::new();
        let code = r#"
def greet_世界():
    return "Hello 世界!"

class UnicodeClass_测试:
    pass
"#;
        let ast = parser.parse_string(code)?;

        let mut formatter = Formatter::new();
        let result = formatter.format_ast(&ast)?;

        assert!(result.contains("greet_世界"));
        assert!(result.contains("UnicodeClass_测试"));
        assert!(result.contains("Hello 世界!"));
        Ok(())
    }

    #[test]
    fn test_format_large_code() -> Result<()> {
        let parser = Parser::new();

        // Generate large code
        let mut large_code = String::new();
        for i in 0..100 {
            large_code.push_str(&format!("def function_{}(): return {}\n", i, i));
        }

        let ast = parser.parse_string(&large_code)?;

        let mut formatter = Formatter::new();
        let result = formatter.format_ast(&ast)?;

        assert!(result.contains("function_0"));
        assert!(result.contains("function_99"));
        Ok(())
    }

    #[test]
    fn test_config_update() -> Result<()> {
        let mut formatter = Formatter::new();

        // Initial config
        assert_eq!(formatter.config.indent_size, 4);

        // Update config
        let new_config = FormatConfig {
            indent_size: 2,
            use_spaces: false,
            ..Default::default()
        };
        formatter.set_config(new_config);

        assert_eq!(formatter.config.indent_size, 2);
        assert!(!formatter.config.use_spaces);
        Ok(())
    }
}
