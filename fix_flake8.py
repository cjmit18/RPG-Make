#!/usr/bin/env python3
"""
Fix common flake8 issues in demo.py
"""

import re
import os

def fix_demo_file():
    """Fix flake8 issues in demo.py"""
    
    with open('demo.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # Fix multiple blank lines (max 2 in a row)
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # Fix common long line patterns - split long string assignments
    content = re.sub(
        r'(\s+)self\.log_message\(f?"([^"]{60,})", "([^"]+)"\)',
        r'\1msg = f"\2"\n\1self.log_message(msg, "\3")',
        content
    )
    
    # Fix long conditional statements
    content = re.sub(
        r'(\s+)if (.{80,}) and (.+):',
        r'\1if (\2 and\n\1        \3):',
        content
    )
    
    # Fix long f-string expressions - break at logical points
    long_fstring_pattern = r'(\s+)(\w+) = f"([^"]{80,})"'
    def replace_long_fstring(match):
        indent = match.group(1)
        var = match.group(2)
        content_str = match.group(3)
        
        # Try to break at obvious points
        if ' for ' in content_str:
            parts = content_str.split(' for ', 1)
            return f'{indent}{var} = f"{parts[0]} for {{}}".format("{parts[1]}")'
        elif ' with ' in content_str:
            parts = content_str.split(' with ', 1)
            return f'{indent}{var} = f"{parts[0]} with {{}}".format("{parts[1]}")'
        elif ': ' in content_str and len(content_str) > 100:
            parts = content_str.split(': ', 1)
            return f'{indent}{var} = f"{parts[0]}: {{}}".format("{parts[1]}")'
        
        return match.group(0)  # No change if we can't split nicely
    
    content = re.sub(long_fstring_pattern, replace_long_fstring, content)
    
    # Remove any empty methods that just have pass or incomplete if/else
    # Fix patterns like:
    # if condition:
    #     
    # else:
    #     
    empty_if_pattern = r'(\s+)if ([^:]+):\s*\n\s*\n\s*else:\s*\n\s*\n'
    content = re.sub(empty_if_pattern, r'\1# TODO: Implement condition: \2\n\1pass\n', content)
    
    # Write back the fixed content
    with open('demo.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed common flake8 issues in demo.py")

if __name__ == "__main__":
    fix_demo_file()
