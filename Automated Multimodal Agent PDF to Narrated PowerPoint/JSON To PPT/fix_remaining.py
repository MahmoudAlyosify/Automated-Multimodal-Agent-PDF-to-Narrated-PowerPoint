#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix remaining Chinese text"""

with open('gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    ('"""增强的图表渲染器，支持更多图表类型和效果"""', '"""Enhanced chart renderer, supports more chart types and effects"""'),
    ('# 绘制网格线', '# Draw grid lines'),
    ('# 绘制柱子', '# Draw bars'),
    ('# 绘制横柱', '# Draw horizontal bars'),
    ('# 绘制折线', '# Draw lines'),
    ('# 绘制点', '# Draw points'),
    ('# 绘制饼图', '# Draw pie'),
    ('# 绘制标签', '# Draw labels'),
    ('# 绘制图例', '# Draw legend'),
    ('# 绘制标题', '# Draw title'),
    ('# 绘制坐标轴', '# Draw axes'),
    ('# 绘制X轴标签', '# Draw X-axis labels'),
    ('# 绘制Y轴标签', '# Draw Y-axis labels'),
    ('# 绘制背景', '# Draw background'),
    ('# 处理数据', '# Process data'),
    ('# 分析数据', '# Analyze data'),
    ('# 计算位置', '# Calculate position'),
    ('# 更新显示', '# Update display'),
    ('# 初始化', '# Initialize'),
    ('# 清理资源', '# Clean up resources'),
]

for old, new in replacements:
    content = content.replace(old, new)

with open('gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed remaining Chinese in gui.py')

# Also fix main.py
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements_main = [
    ('# 增强版', '# Enhanced version'),
    ('# 获取', '# Get'),
    ('# 设置', '# Set'),
    ('# 验证', '# Validate'),
    ('# 处理', '# Handle'),
]

for old, new in replacements_main:
    content = content.replace(old, new)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed main.py')
