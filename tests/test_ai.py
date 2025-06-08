import unittest
from orchestratex.ai import QwenCoder, generate_code
from orchestratex.ai.code_patterns import CodePattern
import torch
import time

class TestQwenCoder(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.coder = QwenCoder(device=self.device)
        self.patterns = CodePattern()
        
    def test_code_generation(self):
        """Test code generation."""
        prompt = "# Write a Python function to calculate factorial"
        result = self.coder.generate_code(prompt)
        self.assertIn("def factorial", result["code"])
        
    def test_code_explanation(self):
        """Test code explanation."""
        code = "def add(a, b): return a + b"
        result = self.coder.explain_code(code)
        self.assertIn("Explanation", result["code"])
        
    def test_code_optimization(self):
        """Test code optimization."""
        code = "def sum_list(lst): return sum(lst)"
        result = self.coder.optimize_code(code)
        self.assertIn("Optimized version", result["code"])
        
    def test_debugging(self):
        """Test debugging assistance."""
        code = "def divide(a, b): return a / b"
        error = "ZeroDivisionError"
        result = self.coder.debug_code(code, error)
        self.assertIn("Debug suggestions", result["code"])
        
    def test_test_case_generation(self):
        """Test test case generation."""
        code = "def multiply(a, b): return a * b"
        result = self.coder.generate_test_cases(code)
        self.assertIn("Test cases", result["code"])
        
    def test_documentation_generation(self):
        """Test documentation generation."""
        code = "def square(x): return x * x"
        result = self.coder.generate_documentation(code)
        self.assertIn("Documentation", result["code"])
        
    def test_pattern_generation(self):
        """Test pattern-based code generation."""
        pattern = self.patterns.get_pattern("design_patterns", "singleton")
        self.assertIsNotNone(pattern)
        
    def test_performance(self):
        """Test code generation performance."""
        prompt = "# Write a Python function to calculate factorial"
        start_time = time.time()
        result = self.coder.generate_code(prompt)
        end_time = time.time()
        self.assertLess(end_time - start_time, 5)  # Should take less than 5 seconds
        
    def test_memory_usage(self):
        """Test memory usage."""
        initial_memory = torch.cuda.memory_allocated(self.device) if self.device == "cuda" else 0
        
        # Generate multiple codes
        for _ in range(10):
            self.coder.generate_code("# Write a simple function")
            
        final_memory = torch.cuda.memory_allocated(self.device) if self.device == "cuda" else 0
        
        # Memory usage should be reasonable
        self.assertLess(final_memory - initial_memory, 1024 * 1024 * 100)  # Less than 100MB increase
        
    def test_cache_behavior(self):
        """Test caching behavior."""
        prompt = "# Write a simple function"
        
        # First generation (should not be cached)
        result1 = self.coder.generate_code(prompt)
        
        # Second generation (should be cached)
        result2 = self.coder.generate_code(prompt)
        
        self.assertEqual(result1["code"], result2["code"])
        
    def test_device_handling(self):
        """Test device handling."""
        if torch.cuda.is_available():
            coder_cuda = QwenCoder(device="cuda")
            result_cuda = coder_cuda.generate_code("# Test CUDA")
            self.assertIsNotNone(result_cuda)
            
        coder_cpu = QwenCoder(device="cpu")
        result_cpu = coder_cpu.generate_code("# Test CPU")
        self.assertIsNotNone(result_cpu)
        
    def test_parameter_tuning(self):
        """Test parameter tuning."""
        prompt = "# Generate random numbers"
        
        # Low temperature (more deterministic)
        result1 = self.coder.generate_code(prompt, temperature=0.2)
        
        # High temperature (more creative)
        result2 = self.coder.generate_code(prompt, temperature=1.5)
        
        self.assertNotEqual(result1["code"], result2["code"])
        
    def test_error_handling(self):
        """Test error handling."""
        with self.assertRaises(Exception):
            self.coder.generate_code(None)
            
        with self.assertRaises(Exception):
            self.coder.generate_code("", max_new_tokens=-1)
            
    def test_pattern_addition(self):
        """Test adding new patterns."""
        new_pattern = {
            "description": "Test pattern",
            "template": "def test(): pass"
        }
        
        result = self.patterns.add_pattern("test", "test_pattern", **new_pattern)
        self.assertTrue(result)
        
    def test_pattern_retrieval(self):
        """Test pattern retrieval."""
        pattern = self.patterns.get_pattern("design_patterns", "singleton")
        self.assertIsNotNone(pattern)
        self.assertIn("description", pattern)
        self.assertIn("template", pattern)
        
    def test_pattern_generation_with_vars(self):
        """Test pattern generation with template variables."""
        pattern = self.patterns.generate_from_pattern(
            "design_patterns",
            "singleton",
            class_name="MySingleton",
            method_name="get_instance"
        )
        self.assertIn("MySingleton", pattern)
        self.assertIn("get_instance", pattern)
        
if __name__ == '__main__':
    unittest.main()
