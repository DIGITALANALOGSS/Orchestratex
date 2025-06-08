import json
from typing import Dict, Any, List
import logging

class CodePattern:
    def __init__(self):
        """Initialize code patterns system."""
        self.logger = logging.getLogger(__name__)
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict[str, Any]:
        """Load predefined code patterns."""
        try:
            with open('data/code_patterns.json', 'r') as f:
                return json.load(f)
        except:
            return self._initialize_default_patterns()
            
    def _initialize_default_patterns(self) -> Dict[str, Any]:
        """Initialize default code patterns."""
        return {
            "design_patterns": {
                "singleton": {
                    "description": "Ensure a class has only one instance",
                    "template": """class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance
                    """
                },
                "observer": {
                    "description": "Define a subscription mechanism",
                    "template": """class Observer:
    def update(self, message):
        pass

class Subject:
    def __init__(self):
        self._observers = []
    
    def add_observer(self, observer):
        self._observers.append(observer)
    
    def remove_observer(self, observer):
        self._observers.remove(observer)
    
    def notify_observers(self, message):
        for observer in self._observers:
            observer.update(message)
                    """
                }
            },
            "data_structures": {
                "binary_tree": {
                    "description": "Binary tree implementation",
                    "template": """class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

def inorder_traversal(root):
    if root:
        inorder_traversal(root.left)
        print(root.value)
        inorder_traversal(root.right)
                    """
                },
                "linked_list": {
                    "description": "Singly linked list",
                    "template": """class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
    
    def append(self, value):
        new_node = Node(value)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
                    """
                }
            },
            "algorithms": {
                "binary_search": {
                    "description": "Binary search algorithm",
                    "template": """def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
                    """
                },
                "quick_sort": {
                    "description": "Quick sort algorithm",
                    "template": """def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
                    """
                }
            }
        }
        
    def get_pattern(self, category: str, pattern_name: str) -> Dict[str, Any]:
        """Get a specific code pattern.
        
        Args:
            category: Pattern category
            pattern_name: Pattern name
            
        Returns:
            Pattern dictionary
        """
        try:
            return self.patterns[category][pattern_name]
        except KeyError:
            self.logger.error(f"Pattern not found: {category}/{pattern_name}")
            return None
            
    def generate_from_pattern(self, category: str, pattern_name: str, **kwargs) -> str:
        """Generate code from a pattern template.
        
        Args:
            category: Pattern category
            pattern_name: Pattern name
            kwargs: Template variables
            
        Returns:
            Generated code
        """
        try:
            pattern = self.get_pattern(category, pattern_name)
            if not pattern:
                return ""
                
            template = pattern["template"]
            for key, value in kwargs.items():
                template = template.replace(f"{{{{ {key} }}}}", str(value))
                
            return template
            
        except Exception as e:
            self.logger.error(f"Pattern generation failed: {str(e)}")
            return ""
            
    def add_pattern(self, category: str, pattern_name: str, description: str, template: str) -> bool:
        """Add a new code pattern.
        
        Args:
            category: Pattern category
            pattern_name: Pattern name
            description: Pattern description
            template: Pattern template
            
        Returns:
            True if pattern added successfully
        """
        try:
            if category not in self.patterns:
                self.patterns[category] = {}
                
            self.patterns[category][pattern_name] = {
                "description": description,
                "template": template
            }
            self._save_patterns()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add pattern: {str(e)}")
            return False
            
    def _save_patterns(self):
        """Save code patterns to file."""
        try:
            with open('data/code_patterns.json', 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save patterns: {str(e)}")
            raise
