import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, Any, Optional, List
import json
import time

class QwenCoder:
    def __init__(self, model_name: str = "Qwen/Qwen2.5-Coder-32B", device: str = "cuda"):
        """Initialize Qwen Coder.
        
        Args:
            model_name: Model name to load
            device: Device to use (cuda or cpu)
        """
        self.logger = logging.getLogger(__name__)
        self.device = device if torch.cuda.is_available() else "cpu"
        self.logger.info(f"Using device: {self.device}")
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        ).eval()
        
        # Cache for recent prompts
        self.prompt_cache = {}
        self.cache_size = 100
        
    def generate_code(self, 
                     prompt: str, 
                     max_new_tokens: int = 256, 
                     temperature: float = 0.7, 
                     top_p: float = 0.95,
                     top_k: int = 50) -> Dict[str, Any]:
        """Generate code using Qwen Coder.
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling probability
            top_k: Top-k sampling
            
        Returns:
            Dictionary containing generated code and metadata
        """
        try:
            # Check cache
            cache_key = f"{prompt}_{max_new_tokens}_{temperature}_{top_p}_{top_k}"
            if cache_key in self.prompt_cache:
                return self.prompt_cache[cache_key]
                
            # Prepare model inputs
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generate code
            with torch.no_grad():
                start_time = time.time()
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                generation_time = time.time() - start_time
                
            # Decode output
            generated_code = self.tokenizer.decode(
                outputs[0][len(inputs["input_ids"][0]):],
                skip_special_tokens=True
            )
            
            # Format response
            response = {
                "code": generated_code,
                "metadata": {
                    "prompt": prompt,
                    "generation_time": generation_time,
                    "device": self.device,
                    "model": self.model.config.name_or_path,
                    "parameters": {
                        "max_new_tokens": max_new_tokens,
                        "temperature": temperature,
                        "top_p": top_p,
                        "top_k": top_k
                    }
                }
            }
            
            # Cache result
            if len(self.prompt_cache) >= self.cache_size:
                self.prompt_cache.pop(next(iter(self.prompt_cache)))
            self.prompt_cache[cache_key] = response
            
            return response
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {str(e)}")
            raise
            
    def explain_code(self, code: str) -> Dict[str, Any]:
        """Generate explanation for code.
        
        Args:
            code: Code to explain
            
        Returns:
            Dictionary containing explanation and metadata
        """
        try:
            prompt = f"# Explain the following code:\n{code}\n# Explanation:\n"
            return self.generate_code(prompt, max_new_tokens=512)
            
        except Exception as e:
            self.logger.error(f"Code explanation failed: {str(e)}")
            raise
            
    def optimize_code(self, code: str) -> Dict[str, Any]:
        """Generate optimized version of code.
        
        Args:
            code: Code to optimize
            
        Returns:
            Dictionary containing optimized code and metadata
        """
        try:
            prompt = f"# Optimize the following code:\n{code}\n# Optimized version:\n"
            return self.generate_code(prompt, max_new_tokens=512)
            
        except Exception as e:
            self.logger.error(f"Code optimization failed: {str(e)}")
            raise
            
    def debug_code(self, code: str, error: str) -> Dict[str, Any]:
        """Generate debugging suggestions for code.
        
        Args:
            code: Code to debug
            error: Error message
            
        Returns:
            Dictionary containing debugging suggestions and metadata
        """
        try:
            prompt = f"# Debug the following code:\n{code}\n# Error: {error}\n# Debug suggestions:\n"
            return self.generate_code(prompt, max_new_tokens=512)
            
        except Exception as e:
            self.logger.error(f"Code debugging failed: {str(e)}")
            raise
            
    def generate_test_cases(self, code: str) -> Dict[str, Any]:
        """Generate test cases for code.
        
        Args:
            code: Code to generate tests for
            
        Returns:
            Dictionary containing test cases and metadata
        """
        try:
            prompt = f"# Write test cases for the following code:\n{code}\n# Test cases:\n"
            return self.generate_code(prompt, max_new_tokens=512)
            
        except Exception as e:
            self.logger.error(f"Test case generation failed: {str(e)}")
            raise
            
    def generate_documentation(self, code: str) -> Dict[str, Any]:
        """Generate documentation for code.
        
        Args:
            code: Code to document
            
        Returns:
            Dictionary containing documentation and metadata
        """
        try:
            prompt = f"# Write documentation for the following code:\n{code}\n# Documentation:\n"
            return self.generate_code(prompt, max_new_tokens=512)
            
        except Exception as e:
            self.logger.error(f"Documentation generation failed: {str(e)}")
            raise
