
from src.parsing.code_chunker import chunk_python_code


def test_function_is_detected():
    code = """
def add(a, b):
    return a + b
"""

    chunks = chunk_python_code(code, "math_utils.py")

    assert len(chunks) == 1
    assert chunks[0]["chunk_name"] == "add"
    assert chunks[0]["chunk_type"] == "function"


def test_class_is_detected():
    code = """
class Calculator:
    def multiply(self, a, b):
        return a * b
"""

    chunks = chunk_python_code(code, "calculator.py")

    assert len(chunks) == 1
    assert chunks[0]["chunk_name"] == "Calculator"
    assert chunks[0]["chunk_type"] == "class"


def test_invalid_python_returns_no_chunks():
    code = "def broken(:"

    chunks = chunk_python_code(code, "broken.py")

    assert chunks == []


def test_module_level_code_is_preserved():
    code = "x = 10\nprint(x)"

    chunks = chunk_python_code(code, "script.py")

    assert len(chunks) == 1
    assert chunks[0]["chunk_type"] == "module"
