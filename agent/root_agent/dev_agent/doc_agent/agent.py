"""
Documentation Agent - Generates and maintains code documentation
"""
import os
import ast
from pathlib import Path
from importlib import import_module


def _ensure_env_loaded() -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        load_dotenv = None

    if load_dotenv:
        load_dotenv()
        return

    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_ensure_env_loaded()


def _load_tool():
    try:
        return getattr(import_module("google.adk.framework.tool"), "tool")
    except Exception:
        def noop_decorator():
            def decorator(func):
                return func
            return decorator
        return noop_decorator


def _load_agent():
    try:
        return getattr(import_module("google.adk.agents.llm_agent"), "Agent")
    except Exception:
        class _Agent:
            def __init__(self, **kwargs):
                self.config = kwargs
        return _Agent


tool = _load_tool()
Agent = _load_agent()


@tool()
async def analyze_python_file(file_path: str) -> str:
    """Analyze a Python file and extract its structure (classes, functions, docstrings)."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File {file_path} not found."
        
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=file_path)
        
        analysis = []
        analysis.append(f"# Documentation Analysis for {path.name}\n")
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node) or "No docstring"
                analysis.append(f"\n## Function: {node.name}")
                analysis.append(f"- Args: {[arg.arg for arg in node.args.args]}")
                analysis.append(f"- Docstring: {docstring[:100]}...")
                
            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node) or "No docstring"
                analysis.append(f"\n## Class: {node.name}")
                analysis.append(f"- Docstring: {docstring[:100]}...")
        
        return "\n".join(analysis)
    
    except Exception as e:
        return f"Error analyzing file: {str(e)}"


@tool()
async def generate_docstring(code_snippet: str) -> str:
    """Generate a docstring suggestion for the given code snippet."""
    try:
        tree = ast.parse(code_snippet)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                return f'''"""
{node.name} function.

Args:
{chr(10).join(f"    {arg}: Description of {arg}" for arg in args)}

Returns:
    Description of return value.
"""'''
        
        return "Unable to parse code snippet. Please provide a valid function or class."
    
    except Exception as e:
        return f"Error generating docstring: {str(e)}"


@tool()
async def check_documentation_coverage(directory_path: str) -> str:
    """Check documentation coverage for Python files in a directory."""
    try:
        path = Path(directory_path)
        if not path.exists():
            return f"Error: Directory {directory_path} not found."
        
        results = []
        total_functions = 0
        documented_functions = 0
        
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(py_file))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_functions += 1
                    if ast.get_docstring(node):
                        documented_functions += 1
        
        if total_functions > 0:
            coverage = (documented_functions / total_functions) * 100
            results.append(f"Documentation Coverage: {coverage:.1f}%")
            results.append(f"Total Functions: {total_functions}")
            results.append(f"Documented: {documented_functions}")
            results.append(f"Missing Docs: {total_functions - documented_functions}")
        else:
            results.append("No functions found in directory.")
        
        return "\n".join(results)
    
    except Exception as e:
        return f"Error checking coverage: {str(e)}"


root_agent = Agent(
    model='gemini-2.5-flash',
    name='doc_agent',
    description='Analyzes code and generates documentation for Python files.',
    instruction='Help developers maintain high-quality documentation by analyzing code structure, generating docstrings, and reporting documentation coverage.',
    tools=[analyze_python_file, generate_docstring, check_documentation_coverage],
)
