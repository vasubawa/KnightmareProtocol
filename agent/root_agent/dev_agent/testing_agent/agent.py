"""
Testing Agent - Generates and runs tests for Python code
"""
import os
import ast
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
async def generate_test_template(file_path: str) -> str:
    """Generate a test template for the given Python file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File {file_path} not found."
        
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=file_path)
        
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        # Generate test file content
        test_content = ['import pytest', f'from {path.stem} import *', '', '']
        
        for func in functions:
            test_content.append(f'def test_{func}():')
            test_content.append(f'    """Test {func} function."""')
            test_content.append('    # TODO: Implement test')
            test_content.append(f'    # result = {func}()')
            test_content.append('    # assert result == expected_value')
            test_content.append('')
        
        for cls in classes:
            test_content.append(f'class Test{cls}:')
            test_content.append(f'    """Test suite for {cls} class."""')
            test_content.append('')
            test_content.append('    def test_init(self):')
            test_content.append(f'        """Test {cls} initialization."""')
            test_content.append('        # TODO: Implement test')
            test_content.append(f'        # instance = {cls}()')
            test_content.append('        # assert instance is not None')
            test_content.append('')
        
        return '\n'.join(test_content)
    
    except Exception as e:
        return f"Error generating test template: {str(e)}"


@tool()
async def run_pytest(directory_path: str = ".") -> str:
    """Run pytest in the specified directory."""
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', directory_path, '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            return f"✓ All tests passed!\n\n{output[:1000]}"
        else:
            return f"✗ Some tests failed:\n\n{output[:1000]}"
    
    except subprocess.TimeoutExpired:
        return "Test execution timed out (>60s)"
    except FileNotFoundError:
        return "pytest not installed. Install with: pip install pytest"
    except Exception as e:
        return f"Error running tests: {str(e)}"


@tool()
async def check_test_coverage(directory_path: str = ".") -> str:
    """Check test coverage using pytest-cov."""
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', '--cov=' + directory_path, '--cov-report=term-missing'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + result.stderr
        
        return f"Test Coverage Report:\n\n{output[:1000]}"
    
    except subprocess.TimeoutExpired:
        return "Coverage check timed out (>60s)"
    except FileNotFoundError:
        return "pytest-cov not installed. Install with: pip install pytest-cov"
    except Exception as e:
        return f"Error checking coverage: {str(e)}"


@tool()
async def analyze_test_files(directory_path: str) -> str:
    """Analyze test files and provide statistics."""
    try:
        path = Path(directory_path)
        if not path.exists():
            return f"Error: Directory {directory_path} not found."
        
        test_files = list(path.rglob("test_*.py")) + list(path.rglob("*_test.py"))
        
        total_tests = 0
        total_files = len(test_files)
        
        for test_file in test_files:
            content = test_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(test_file))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    total_tests += 1
        
        result = [f"Test Analysis for {directory_path}:"]
        result.append(f"Total test files: {total_files}")
        result.append(f"Total test functions: {total_tests}")
        
        if total_files > 0:
            result.append(f"Average tests per file: {total_tests / total_files:.1f}")
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error analyzing tests: {str(e)}"


root_agent = Agent(
    model='gemini-2.5-flash',
    name='testing_agent',
    description='Generates test templates, runs tests, and analyzes test coverage for Python code.',
    instruction='Help developers maintain high test quality by generating test templates, running pytest, checking coverage, and analyzing test suites.',
    tools=[generate_test_template, run_pytest, check_test_coverage, analyze_test_files],
)
