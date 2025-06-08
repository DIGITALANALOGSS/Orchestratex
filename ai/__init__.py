from .qwen_coder import QwenCoder

def get_qwen_coder(device: str = "cuda") -> QwenCoder:
    """Get Qwen Coder instance.
    
    Args:
        device: Device to use (cuda or cpu)
        
    Returns:
        QwenCoder instance
    """
    return QwenCoder(device=device)

def generate_code(prompt: str, 
                 max_new_tokens: int = 256, 
                 temperature: float = 0.7, 
                 top_p: float = 0.95,
                 top_k: int = 50,
                 device: str = "cuda") -> Dict[str, Any]:
    """Generate code using Qwen Coder.
    
    Args:
        prompt: Input prompt
        max_new_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature
        top_p: Top-p sampling probability
        top_k: Top-k sampling
        device: Device to use (cuda or cpu)
        
    Returns:
        Dictionary containing generated code and metadata
    """
    coder = get_qwen_coder(device)
    return coder.generate_code(
        prompt=prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k
    )
