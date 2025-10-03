"""
Test all template files for syntax errors
"""

import os
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError

def test_all_templates():
    template_dir = 'templates'
    env = Environment(loader=FileSystemLoader(template_dir))
    
    errors = []
    success = []
    
    # Get all HTML files
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                template_path = os.path.relpath(os.path.join(root, file), template_dir)
                # Convert Windows backslashes to forward slashes for Jinja2
                template_path = template_path.replace('\\', '/')
                try:
                    env.get_template(template_path)
                    success.append(template_path)
                    print(f"✅ {template_path}")
                except TemplateSyntaxError as e:
                    errors.append((template_path, str(e)))
                    print(f"❌ {template_path}: {e}")
                except Exception as e:
                    errors.append((template_path, str(e)))
                    print(f"⚠️  {template_path}: {e}")
    
    print("\n" + "="*70)
    print(f"✅ {len(success)} templates passed")
    print(f"❌ {len(errors)} templates failed")
    print("="*70)
    
    if errors:
        print("\nErrors:")
        for template, error in errors:
            print(f"  - {template}: {error}")
        return False
    else:
        print("\n🎉 All templates have valid syntax!")
        return True

if __name__ == '__main__':
    test_all_templates()