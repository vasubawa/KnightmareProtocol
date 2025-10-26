"""
Linter Agent - Performs code quality checks and linting
"""
import os
import subprocess
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
async def check_python_syntax(file_path: str) -> str:
    """Check Python file for syntax errors."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File {file_path} not found."
        
        content = path.read_text(encoding="utf-8")
        compile(content, file_path, 'exec')
        
        return f"✓ {path.name} has valid Python syntax."
    
    except SyntaxError as e:
        return f"✗ Syntax error in {file_path}:\n  Line {e.lineno}: {e.msg}\n  {e.text}"
    except Exception as e:
        return f"Error checking syntax: {str(e)}"


@tool()
async def run_basic_linter(file_path: str) -> str:
    """Run basic linting checks on a Python file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File {file_path} not found."
        
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        issues = []
        
        # Check line length
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append(f"Line {i}: Line too long ({len(line)} > 120 characters)")
        
        # Check for trailing whitespace
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line:
                issues.append(f"Line {i}: Trailing whitespace")
        
        # Check for multiple blank lines
        blank_count = 0
        for i, line in enumerate(lines, 1):
            if not line.strip():
                blank_count += 1
                if blank_count > 2:
                    issues.append(f"Line {i}: More than 2 consecutive blank lines")
            else:
                blank_count = 0
        
        if issues:
            return f"Linting issues found in {path.name}:\n" + "\n".join(issues[:10])
        else:
            return f"✓ No basic linting issues found in {path.name}."
    
    except Exception as e:
        return f"Error during linting: {str(e)}"


@tool()
async def run_pylint(file_path: str) -> str:
    """Run pylint on a Python file if available."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File {file_path} not found."
        
        # Try to run pylint
        result = subprocess.run(
            ['python', '-m', 'pylint', str(path), '--score=yes'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        if result.returncode == 0:
            return f"✓ Pylint check passed for {path.name}:\n{output[:500]}"
        else:
            return f"Pylint issues found in {path.name}:\n{output[:500]}"
    
    except subprocess.TimeoutExpired:
        return "Pylint check timed out (>30s)"
    except FileNotFoundError:
        return "Pylint not installed. Using basic linter instead. Install with: pip install pylint"
    except Exception as e:
        return f"Error running pylint: {str(e)}"


@tool()
async def check_code_complexity(file_path: str) -> str:
    """Analyze code complexity (cyclomatic complexity approximation)."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File {file_path} not found."
        
        content = path.read_text(encoding="utf-8")
        
        # Simple complexity metrics
        complexity_keywords = ['if', 'elif', 'for', 'while', 'except', 'and', 'or']
        lines = content.splitlines()
        
        total_complexity = 0
        complex_functions = []
        
        current_function = None
        function_complexity = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Detect function start
            if stripped.startswith('def '):
                if current_function and function_complexity > 10:
                    complex_functions.append(f"{current_function}: complexity ~{function_complexity}")
                current_function = stripped.split('(')[0].replace('def ', '')
                function_complexity = 1
            
            # Count complexity keywords
            for keyword in complexity_keywords:
                if f' {keyword} ' in f' {stripped} ' or f' {keyword}(' in stripped:
                    function_complexity += 1
                    total_complexity += 1
        
        # Check last function
        if current_function and function_complexity > 10:
            complex_functions.append(f"{current_function}: complexity ~{function_complexity}")
        
        result = [f"Code Complexity Analysis for {path.name}:"]
        result.append(f"Total complexity score: ~{total_complexity}")
        
        if complex_functions:
            result.append("\nComplex functions (>10):")
            result.extend(complex_functions)
        else:
            result.append("✓ No overly complex functions detected.")
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error analyzing complexity: {str(e)}"


root_agent = Agent(
    model='gemini-2.5-flash',
    name='linter_agent',
    description='Performs code quality checks, linting, and complexity analysis on Python files.',
    instruction='Help developers maintain clean, readable code by detecting syntax errors, style issues, and complexity problems.',
    tools=[check_python_syntax, run_basic_linter, run_pylint, check_code_complexity],
)
