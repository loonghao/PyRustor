//! AST node type definitions

use serde::{Deserialize, Serialize};
use std::fmt;

/// Reference to an AST node for low-level operations
#[derive(Debug, Clone)]
pub struct AstNodeRef {
    /// Index path to the node in the AST
    pub path: Vec<usize>,
    /// Type of the node
    pub node_type: String,
    /// Source location information
    pub location: Option<SourceLocation>,
}

/// Source code location
#[derive(Debug, Clone)]
pub struct SourceLocation {
    pub line: usize,
    pub column: usize,
}

/// Import node information
#[derive(Debug, Clone)]
pub struct ImportNode {
    /// The import statement
    pub module: String,
    /// Imported items (for 'from' imports)
    pub items: Vec<String>,
    /// Node reference
    pub node_ref: AstNodeRef,
}

/// Function call node information
#[derive(Debug, Clone)]
pub struct CallNode {
    /// Function name
    pub function_name: String,
    /// Arguments (simplified)
    pub args: Vec<String>,
    /// Node reference
    pub node_ref: AstNodeRef,
}

/// Try-except block information
#[derive(Debug, Clone)]
pub struct TryExceptNode {
    /// Exception types handled
    pub exception_types: Vec<String>,
    /// Node reference
    pub node_ref: AstNodeRef,
}

/// Assignment node information
#[derive(Debug, Clone)]
pub struct AssignmentNode {
    /// Target variable name
    pub target: String,
    /// Value expression (simplified)
    pub value: String,
    /// Node reference
    pub node_ref: AstNodeRef,
}

/// Information about an import statement
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ImportInfo {
    /// The imported module or name
    pub module: String,
    /// Optional alias for the import
    pub alias: Option<String>,
    /// Whether this is a "from ... import ..." statement
    pub is_from_import: bool,
    /// The module being imported from (for "from ... import ..." statements)
    pub from_module: Option<String>,
}

/// Trait for AST nodes that have location information
pub trait HasLocation {
    /// Get the line number where this node starts
    fn line_number(&self) -> Option<usize>;

    /// Get the column number where this node starts
    fn column_number(&self) -> Option<usize>;
}

impl fmt::Display for ImportInfo {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if self.is_from_import {
            if let Some(from_module) = &self.from_module {
                write!(f, "from {} import {}", from_module, self.module)?;
            } else {
                write!(f, "from . import {}", self.module)?;
            }
        } else {
            write!(f, "import {}", self.module)?;
        }

        if let Some(alias) = &self.alias {
            write!(f, " as {}", alias)?;
        }

        Ok(())
    }
}
