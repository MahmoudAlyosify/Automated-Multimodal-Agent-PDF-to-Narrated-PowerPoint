#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find all lines with Chinese characters
import re
for i, line in enumerate(lines, 1):
    if re.search(r'[\u4e00-\u9fff]', line):
        print(f"Line {i}: {line.rstrip()}")
