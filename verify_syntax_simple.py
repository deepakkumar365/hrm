import ast
import sys

try:
    with open('D:/Projects/HRMS/hrm/routes.py', 'r') as f:
        code = f.read()
    
    ast.parse(code)
    print("✅ routes.py syntax is VALID!")
    print(f"File has {len(code.splitlines())} lines")
    
except SyntaxError as e:
    print(f"❌ SyntaxError found:")
    print(f"  Line {e.lineno}: {e.msg}")
    print(f"  {e.text}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)