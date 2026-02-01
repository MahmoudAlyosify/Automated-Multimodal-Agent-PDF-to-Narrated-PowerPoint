#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive translation from Chinese to English"""

# Extended list of replacements including data strings
replacements = [
    # Headers and comments
    ('# 增强版 gui.py', '# Enhanced gui.py'),
    ('# 导入main.py中的函数', '# Import functions from main.py'),
    ('# 常量定义', '# Constant definitions'),
    ('# 配色方案', '# Color scheme'),
    ('# 图表默认颜色', '# Default chart colors'),
    ('# 增强的示例JSON', '# Enhanced sample JSON'),
    ('# 增强的图表渲染器，支持更多图表类型和效果', '# Enhanced chart renderer, supports more chart types and effects'),
    ('"""加载字体，优先支持中文"""', '"""Load fonts, prioritize Chinese support"""'),
    ('"""渲染图表"""', '"""Render chart"""'),
    ('# 外框', '# Outer frame'),
    ('# 字体', '# Font'),
    ('# 根据类型分发', '# Dispatch by type'),
    ('"""绘制柱状图"""', '"""Draw bar chart"""'),
    ('"""绘制折线图"""', '"""Draw line chart"""'),
    ('"""绘制饼图"""', '"""Draw pie chart"""'),
    ('"""绘制散点图"""', '"""Draw scatter chart"""'),
    ('# 绘制坐标轴', '# Draw axes'),
    ('# 绘制标题', '# Draw title'),
    ('# 绘制图例', '# Draw legend'),
    ('"""绘制柱子"""', '"""Draw bar"""'),
    ('"""绘制点"""', '"""Draw points"""'),
    ('"""绘制连线"""', '"""Draw lines"""'),
    ('# 绘制背景网格', '# Draw background grid'),
    ('"""加载示例数据"""', '"""Load sample data"""'),
    ('"""主窗口类"""', '"""Main window class"""'),
    ('"""初始化UI"""', '"""Initialize UI"""'),
    ('"""处理JSON输入变化"""', '"""Handle JSON input change"""'),
    ('"""更新幻灯片预览"""', '"""Update slide preview"""'),
    ('"""生成PPTX文件"""', '"""Generate PPTX file"""'),
    ('"""更新幻灯片列表""', '"""Update slide list"""'),
    ('"""导入JSON文件"""', '"""Import JSON file"""'),
    ('"""导出PPTX文件"""', '"""Export PPTX file"""'),
    ('"""显示帮助信息"""', '"""Show help information"""'),
    ('"""处理错误消息"""', '"""Handle error messages"""'),
    ('"""处理成功消息"""', '"""Handle success messages"""'),
    ('"""显示关于对话框"""', '"""Show about dialog"""'),
    ('"""更新日志显示"""', '"""Update log display"""'),
    ('"""清空日志"""', '"""Clear logs"""'),
    ('"""启动应用"""', '"""Start application"""'),
    ('# 预览失败:', '# Preview failed:'),
    ('预览失败: ', 'Preview failed: '),
    ('# 生成PPTX文件失败', '# Failed to generate PPTX file'),
    ('生成PPTX失败: ', 'Failed to generate PPTX: '),
    ('PPTX生成成功: ', 'PPTX generated successfully: '),
    ('# 更新幻灯片列表', '# Update slide list'),
    ('构建PPT失败: ', 'Failed to build PPT: '),
    ('预览生成失败:', 'Preview generation failed:'),
    ('# 保存文件选择', '# Save file selection'),
    ('保存为: ', 'Saved as: '),
    # Sample data strings
    ('"title": "欢迎",', '"title": "Welcome",'),
    ('"text": "JSON → PPT 设计器"', '"text": "JSON to PPT Designer"'),
    ('"title": "多元素展示"', '"title": "Multi-Element Display"'),
    ('"text": "组合元素"', '"text": "Combined Elements"'),
    ('"text": "开始"', '"text": "Start"'),
    ('"text": "过程"', '"text": "Process"'),
    ('"text": "结束"', '"text": "End"'),
    # Error and warning messages
    ('警告: ', 'Warning: '),
    ('错误: ', 'Error: '),
    ('成功', 'Success'),
    ('失败', 'Failed'),
    ('信息', 'Information'),
]

def translate_file(filepath):
    """Translate Chinese to English in the given file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Successfully translated {filepath}")
    except Exception as e:
        print(f"Error translating {filepath}: {e}")

if __name__ == '__main__':
    translate_file('main.py')
    translate_file('gui.py')
