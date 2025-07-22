#!/usr/bin/env python3
"""
Performance testing script for PyRustor.

This script runs comprehensive performance tests and generates
detailed reports for benchmarking and regression detection.
"""

import time
import sys
import json
import statistics
from pathlib import Path
from typing import Dict, List, Any
import pyrustor


class PerformanceTimer:
    """Simple performance timer context manager."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.perf_counter()
    
    @property
    def elapsed(self) -> float:
        if self.start_time is None or self.end_time is None:
            return 0.0
        return self.end_time - self.start_time


def generate_large_code(num_functions: int, num_classes: int) -> str:
    """Generate large Python code for testing."""
    lines = []
    
    # Add imports
    lines.extend([
        "import os",
        "import sys",
        "from typing import List, Dict, Optional",
        "from pathlib import Path",
        "",
    ])
    
    # Add functions
    for i in range(num_functions):
        lines.extend([
            f"def function_{i}(param1, param2={i}):",
            f"    '''Function {i} documentation.'''",
            f"    result = param1 + param2 + {i}",
            f"    return result * {i % 10 + 1}",
            "",
        ])
    
    # Add classes
    for i in range(num_classes):
        lines.extend([
            f"class Class_{i}:",
            f"    '''Class {i} documentation.'''",
            f"    ",
            f"    def __init__(self, value={i}):",
            f"        self.value = value",
            f"        self.data = [x for x in range({i % 10 + 1})]",
            f"    ",
            f"    def method_{i}(self):",
            f"        return self.value * {i % 5 + 1}",
            f"    ",
            f"    def process_data(self):",
            f"        return sum(self.data) + self.value",
            "",
        ])
    
    return "\n".join(lines)


def benchmark_parsing(code: str, iterations: int = 10) -> Dict[str, Any]:
    """Benchmark parsing performance."""
    parser = pyrustor.Parser()
    times = []
    
    for _ in range(iterations):
        with PerformanceTimer() as timer:
            ast = parser.parse_string(code)
        times.append(timer.elapsed)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0.0,
        "iterations": iterations,
        "code_size": len(code),
        "lines": code.count('\n') + 1,
    }


def benchmark_refactoring(code: str, iterations: int = 5) -> Dict[str, Any]:
    """Benchmark refactoring performance."""
    parser = pyrustor.Parser()
    ast = parser.parse_string(code)
    
    times = []
    
    for i in range(iterations):
        # Create a fresh refactor instance for each iteration
        refactor = pyrustor.Refactor(ast)
        
        with PerformanceTimer() as timer:
            # Perform multiple refactoring operations
            refactor.rename_function(f"function_0", f"renamed_function_0_{i}")
            if i < 10:  # Only rename first 10 classes to avoid errors
                refactor.rename_class(f"Class_0", f"RenamedClass_0_{i}")
            refactor.modernize_syntax()
            result = refactor.get_code()
        
        times.append(timer.elapsed)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0.0,
        "iterations": iterations,
        "code_size": len(code),
        "lines": code.count('\n') + 1,
    }


def benchmark_code_generation(code: str, iterations: int = 10) -> Dict[str, Any]:
    """Benchmark code generation performance."""
    parser = pyrustor.Parser()
    ast = parser.parse_string(code)
    refactor = pyrustor.Refactor(ast)
    
    times = []
    
    for _ in range(iterations):
        with PerformanceTimer() as timer:
            result = refactor.get_code()
        times.append(timer.elapsed)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0.0,
        "iterations": iterations,
        "code_size": len(code),
        "lines": code.count('\n') + 1,
        "output_size": len(result) if 'result' in locals() else 0,
    }


def run_performance_suite() -> Dict[str, Any]:
    """Run comprehensive performance test suite."""
    print("🚀 Starting PyRustor performance test suite...")
    
    results = {
        "timestamp": time.time(),
        "version": pyrustor.__version__,
        "benchmarks": {}
    }
    
    # Test different code sizes
    test_cases = [
        ("small", 10, 5),      # 10 functions, 5 classes
        ("medium", 50, 25),    # 50 functions, 25 classes
        ("large", 200, 100),   # 200 functions, 100 classes
    ]
    
    for size_name, num_functions, num_classes in test_cases:
        print(f"\n📊 Testing {size_name} codebase ({num_functions} functions, {num_classes} classes)...")
        
        # Generate test code
        code = generate_large_code(num_functions, num_classes)
        print(f"   Generated {len(code):,} characters, {code.count(chr(10)) + 1:,} lines")
        
        # Run benchmarks
        print("   🔍 Benchmarking parsing...")
        parsing_results = benchmark_parsing(code, iterations=10)
        
        print("   🔧 Benchmarking refactoring...")
        refactoring_results = benchmark_refactoring(code, iterations=5)
        
        print("   📝 Benchmarking code generation...")
        generation_results = benchmark_code_generation(code, iterations=10)
        
        results["benchmarks"][size_name] = {
            "parsing": parsing_results,
            "refactoring": refactoring_results,
            "code_generation": generation_results,
            "metadata": {
                "functions": num_functions,
                "classes": num_classes,
                "code_size": len(code),
                "lines": code.count('\n') + 1,
            }
        }
        
        # Print summary
        print(f"   ✅ Parsing: {parsing_results['mean']:.3f}s ± {parsing_results['std']:.3f}s")
        print(f"   ✅ Refactoring: {refactoring_results['mean']:.3f}s ± {refactoring_results['std']:.3f}s")
        print(f"   ✅ Code Gen: {generation_results['mean']:.3f}s ± {generation_results['std']:.3f}s")
    
    return results


def save_results(results: Dict[str, Any], output_file: str = "performance_results.json"):
    """Save performance results to JSON file."""
    output_path = Path(output_file)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to {output_path}")


def print_summary(results: Dict[str, Any]):
    """Print performance summary."""
    print("\n" + "="*60)
    print("📈 PERFORMANCE SUMMARY")
    print("="*60)
    
    for size_name, benchmark in results["benchmarks"].items():
        print(f"\n{size_name.upper()} CODEBASE:")
        print(f"  Functions: {benchmark['metadata']['functions']}")
        print(f"  Classes: {benchmark['metadata']['classes']}")
        print(f"  Lines: {benchmark['metadata']['lines']:,}")
        print(f"  Size: {benchmark['metadata']['code_size']:,} chars")
        print(f"  Parsing: {benchmark['parsing']['mean']:.3f}s")
        print(f"  Refactoring: {benchmark['refactoring']['mean']:.3f}s")
        print(f"  Code Gen: {benchmark['code_generation']['mean']:.3f}s")
    
    print("\n" + "="*60)


def main():
    """Main performance testing function."""
    try:
        results = run_performance_suite()
        print_summary(results)
        save_results(results)
        
        print("\n🎉 Performance testing completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n💥 Performance testing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
