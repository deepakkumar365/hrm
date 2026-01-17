import py_compile
import sys

try:
    py_compile.compile('d:/Project/Workouts/hrm/routes/routes_ot.py', doraise=True)
    print("Syntax OK")
except py_compile.PyCompileError as e:
    print(f"Syntax Error: {e}")
except Exception as e:
    print(f"Error: {e}")
