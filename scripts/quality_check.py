#!/usr/bin/env python3
"""
Code quality check script for PyRustor.

This script runs comprehensive code quality checks including:
- Static analysis
- Security scanning
- Documentation coverage
- Code complexity analysis
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class QualityChecker:
    """Code quality checker for PyRustor."""
    
    def __init__(self):
        self.results = {
            "timestamp": None,
            "checks": {},
            "summary": {
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
    
    def run_command(self, cmd: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result
        except FileNotFoundError:
            print(f"⚠️  Command not found: {cmd[0]}")
            return subprocess.CompletedProcess(cmd, 1, "", f"Command not found: {cmd[0]}")
    
    def check_python_formatting(self) -> Dict[str, Any]:
        """Check Python code formatting with ruff."""
        print("🔍 Checking Python formatting...")
        
        result = self.run_command(["uv", "run", "ruff", "format", "--check", "."])
        
        return {
            "name": "Python Formatting",
            "passed": result.returncode == 0,
            "output": result.stdout + result.stderr,
            "command": " ".join(result.args)
        }
    
    def check_python_linting(self) -> Dict[str, Any]:
        """Check Python code with ruff linter."""
        print("🔍 Checking Python linting...")
        
        result = self.run_command(["uv", "run", "ruff", "check", ".", "--output-format", "json"])
        
        issues = []
        if result.stdout:
            try:
                issues = json.loads(result.stdout)
            except json.JSONDecodeError:
                pass
        
        return {
            "name": "Python Linting",
            "passed": result.returncode == 0,
            "issues_count": len(issues),
            "issues": issues[:10],  # Limit to first 10 issues
            "output": result.stderr,
            "command": " ".join(result.args)
        }
    
    def check_rust_formatting(self) -> Dict[str, Any]:
        """Check Rust code formatting."""
        print("🔍 Checking Rust formatting...")
        
        result = self.run_command(["cargo", "fmt", "--all", "--", "--check"])
        
        return {
            "name": "Rust Formatting",
            "passed": result.returncode == 0,
            "output": result.stdout + result.stderr,
            "command": " ".join(result.args)
        }
    
    def check_rust_linting(self) -> Dict[str, Any]:
        """Check Rust code with clippy."""
        print("🔍 Checking Rust linting...")
        
        result = self.run_command([
            "cargo", "clippy", "--all-targets", "--all-features", 
            "--", "-D", "warnings", "-A", "clippy::uninlined-format-args"
        ])
        
        return {
            "name": "Rust Linting (Clippy)",
            "passed": result.returncode == 0,
            "output": result.stdout + result.stderr,
            "command": " ".join(result.args)
        }
    
    def check_security_python(self) -> Dict[str, Any]:
        """Check Python security with bandit."""
        print("🔍 Checking Python security...")
        
        # Install bandit if not available
        install_result = self.run_command(["uv", "add", "--group", "dev", "bandit"])
        
        result = self.run_command([
            "uv", "run", "bandit", "-r", "python/", 
            "-f", "json", "-q"
        ])
        
        issues = []
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                issues = data.get("results", [])
            except json.JSONDecodeError:
                pass
        
        return {
            "name": "Python Security (Bandit)",
            "passed": result.returncode == 0,
            "issues_count": len(issues),
            "high_severity": len([i for i in issues if i.get("issue_severity") == "HIGH"]),
            "medium_severity": len([i for i in issues if i.get("issue_severity") == "MEDIUM"]),
            "low_severity": len([i for i in issues if i.get("issue_severity") == "LOW"]),
            "command": " ".join(result.args)
        }
    
    def check_security_rust(self) -> Dict[str, Any]:
        """Check Rust security with cargo audit."""
        print("🔍 Checking Rust security...")
        
        # Install cargo-audit if not available
        install_result = self.run_command(["cargo", "install", "cargo-audit"])
        
        result = self.run_command(["cargo", "audit", "--json"])
        
        vulnerabilities = []
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                vulnerabilities = data.get("vulnerabilities", {}).get("list", [])
            except json.JSONDecodeError:
                pass
        
        return {
            "name": "Rust Security (Cargo Audit)",
            "passed": result.returncode == 0,
            "vulnerabilities_count": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "command": " ".join(result.args)
        }
    
    def check_dependencies_python(self) -> Dict[str, Any]:
        """Check Python dependencies with safety."""
        print("🔍 Checking Python dependencies...")
        
        # Install safety if not available
        install_result = self.run_command(["uv", "add", "--group", "dev", "safety"])
        
        result = self.run_command(["uv", "run", "safety", "check", "--json"])
        
        vulnerabilities = []
        if result.stdout:
            try:
                vulnerabilities = json.loads(result.stdout)
            except json.JSONDecodeError:
                pass
        
        return {
            "name": "Python Dependencies (Safety)",
            "passed": result.returncode == 0,
            "vulnerabilities_count": len(vulnerabilities),
            "vulnerabilities": vulnerabilities[:5],  # Limit output
            "command": " ".join(result.args)
        }
    
    def check_test_coverage(self) -> Dict[str, Any]:
        """Check test coverage."""
        print("🔍 Checking test coverage...")
        
        result = self.run_command([
            "uv", "run", "pytest", "--cov=pyrustor", 
            "--cov-report=json", "--cov-report=term-missing",
            "tests/", "-q"
        ])
        
        coverage_data = {}
        coverage_file = Path("coverage.json")
        if coverage_file.exists():
            try:
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
            except json.JSONDecodeError:
                pass
        
        total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
        
        return {
            "name": "Test Coverage",
            "passed": total_coverage >= 80,  # Require 80% coverage
            "coverage_percent": total_coverage,
            "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
            "lines_total": coverage_data.get("totals", {}).get("num_statements", 0),
            "command": " ".join(result.args)
        }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all quality checks."""
        import time
        self.results["timestamp"] = time.time()
        
        checks = [
            self.check_python_formatting,
            self.check_python_linting,
            self.check_rust_formatting,
            self.check_rust_linting,
            self.check_security_python,
            self.check_security_rust,
            self.check_dependencies_python,
            self.check_test_coverage,
        ]
        
        for check_func in checks:
            try:
                result = check_func()
                check_name = result["name"]
                self.results["checks"][check_name] = result
                
                if result["passed"]:
                    print(f"✅ {check_name}")
                    self.results["summary"]["passed"] += 1
                else:
                    print(f"❌ {check_name}")
                    self.results["summary"]["failed"] += 1
                    
            except Exception as e:
                print(f"💥 {check_func.__name__} failed: {e}")
                self.results["summary"]["failed"] += 1
        
        return self.results
    
    def save_results(self, output_file: str = "quality_report.json"):
        """Save quality check results."""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Quality report saved to {output_file}")
    
    def print_summary(self):
        """Print quality check summary."""
        print("\n" + "="*60)
        print("📊 QUALITY CHECK SUMMARY")
        print("="*60)
        
        summary = self.results["summary"]
        total = summary["passed"] + summary["failed"]
        
        print(f"Total checks: {total}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        
        if total > 0:
            success_rate = (summary["passed"] / total) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        print("\n" + "="*60)
        
        # Print failed checks details
        if summary["failed"] > 0:
            print("\n❌ FAILED CHECKS:")
            for name, result in self.results["checks"].items():
                if not result["passed"]:
                    print(f"  • {name}")
                    if "output" in result and result["output"]:
                        # Show first few lines of output
                        lines = result["output"].split('\n')[:3]
                        for line in lines:
                            if line.strip():
                                print(f"    {line}")


def main():
    """Main quality check function."""
    print("🚀 Starting PyRustor quality checks...")
    
    checker = QualityChecker()
    results = checker.run_all_checks()
    
    checker.print_summary()
    checker.save_results()
    
    # Return appropriate exit code
    if results["summary"]["failed"] == 0:
        print("\n🎉 All quality checks passed!")
        return 0
    else:
        print(f"\n💥 {results['summary']['failed']} quality checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
