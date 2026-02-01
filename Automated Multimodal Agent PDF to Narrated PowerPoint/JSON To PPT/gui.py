# Enhanced gui.py
import io
import json
import logging
import os
import time
import tempfile
import math
import copy
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple
import platform

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter, ImageOps

# Import functions from main.py
from main import build, build_single_slide, get_image_bytes, validate, hex_to_rgb

logger = logging.getLogger("json_to_ppt_gui")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Constant definitions
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
PREVIEW_MAX_WIDTH = 960
PREVIEW_MAX_HEIGHT = 540
DEBOUNCE_MS = 300

# Color scheme
COLOR_BG = "#f8f9fa"
COLOR_SIDEBAR = "#2c3e50"
COLOR_CANVAS_BG = "#ffffff"
COLOR_ERROR = "#e74c3c"
COLOR_SUCCESS = "#27ae60"
COLOR_WARNING = "#f39c12"
COLOR_INFO = "#3498db"
COLOR_ACCENT = "#5b7dea"
COLOR_TEXT = "#2c3e50"
COLOR_TEXT_LIGHT = "#7f8c8d"
COLOR_BORDER = "#dce1e7"

# Default chart colors
CHART_COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EF4444", "#06B6D4", "#EC4899", "#6366F1"]

# Enhanced sample JSON
SAMPLE_JSON = json.dumps(
    {
        "version": "1.0",
        "ppt": {
            "size": {"width": DEFAULT_WIDTH, "height": DEFAULT_HEIGHT, "unit": "px"},
            "defaultUnit": "px",
            "theme": {
                "colors": {
                    "primary": "#3B82F6",
                    "secondary": "#10B981",
                    "accent": "#F59E0B",
                    "danger": "#EF4444"
                },
                "fonts": {
                    "heading": "Microsoft YaHei",
                    "body": "Arial"
                }
            },
            "slides": [
                {
                    "id": "slide-1",
                    "title": "Welcome",
                    "background": {
                        "gradient": {
                            "type": "linear",
                            "angle": 45,
                            "stops": [
                                {"color": "#667eea", "position": 0},
                                {"color": "#764ba2", "position": 100}
                            ]
                        }
                    },
                    "transition": {"type": "fade", "duration": 1},
                    "elements": [
                        {
                            "type": "text",
                            "text": "JSON to PPT Designer",
                            "box": {"x": 640, "y": 200, "w": 600, "h": 100},
                            "style": {"fontSize": 48, "align": "center", "color": "#ffffff", "bold": True},
                            "shadow": {"x": 2, "y": 2, "blur": 4, "color": "#00000040"},
                            "rotation": -2
                        },
                        {
                            "type": "shape",
                            "shapeType": "star",
                            "box": {"x": 100, "y": 100, "w": 100, "h": 100},
                            "fill": "#ffd700",
                            "rotation": 15,
                            "shadow": {"x": 3, "y": 3, "blur": 6, "color": "#00000030"}
                        },
                        {
                            "type": "line",
                            "points": [{"x": 200, "y": 400}, {"x": 1080, "y": 400}],
                            "stroke": "#ffffff",
                            "strokeWidth": 2,
                            "strokeStyle": "dashed"
                        }
                    ],
                },
                {
                    "id": "slide-2",
                    "title": "Multi-Element Display",
                    "background": {"color": "#f7fafc"},
                    "elements": [
                        {
                            "type": "group",
                            "box": {"x": 50, "y": 50, "w": 300, "h": 200},
                            "elements": [
                                {
                                    "type": "shape",
                                    "shapeType": "roundRect",
                                    "box": {"x": 0, "y": 0, "w": 300, "h": 200},
                                    "fill": "#e6f7ff",
                                    "border": {"width": 2, "color": "#1890ff", "style": "solid"}
                                },
                                {
                                    "type": "text",
                                    "text": "Combined Elements",
                                    "box": {"x": 150, "y": 100, "w": 200, "h": 50},
                                    "style": {"fontSize": 24, "align": "center", "color": "#1890ff"}
                                }
                            ]
                        },
                        {
                            "type": "icon",
                            "icon": {"library": "fontawesome", "name": "star"},
                            "box": {"x": 400, "y": 100, "w": 60, "h": 60},
                            "color": "#ffd700"
                        },
                        {
                            "type": "smartArt",
                            "smartArtType": "process",
                            "box": {"x": 100, "y": 300, "w": 1080, "h": 300},
                            "nodes": [
                                {"text": "Start", "color": "#3B82F6"},
                                {"text": "Process", "color": "#10B981"},
                                {"text": "End", "color": "#F59E0B"}
                            ]
                        }
                    ]
                }
            ],
        },
    },
    ensure_ascii=False,
    indent=2,
)


class EnhancedChartRenderer:
    """Enhanced chart renderer, supports more chart types and effects"""

    _font_cache: Dict[str, ImageFont.ImageFont] = {}

    @staticmethod
    def _load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
        """Load fonts, prioritize Chinese support"""
        key = f"{size}-{1 if bold else 0}"
        cached = EnhancedChartRenderer._font_cache.get(key)
        if cached:
            return cached

        candidates = [
            os.path.join(os.environ.get("WINDIR", r"C:\\Windows"), "Fonts", "msyh.ttc"),
            os.path.join(os.environ.get("WINDIR", r"C:\\Windows"), "Fonts", "msyhbd.ttc") if bold else "",
            os.path.join(os.environ.get("WINDIR", r"C:\\Windows"), "Fonts", "simhei.ttf"),
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/Library/Fonts/Microsoft YaHei.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "arial.ttf",
        ]

        for path in candidates:
            if not path:
                continue
            try:
                font = ImageFont.truetype(path, size)
                EnhancedChartRenderer._font_cache[key] = font
                return font
            except Exception:
                continue

        font = ImageFont.load_default()
        EnhancedChartRenderer._font_cache[key] = font
        return font

    @staticmethod
    def render_chart(chart_type: str, data: Dict, width: int, height: int,
                     title: str = "", options: Dict = None) -> Image.Image:
        """Render chart"""
        img = Image.new('RGBA', (max(120, width), max(80, height)), color='white')
        draw = ImageDraw.Draw(img)

        # Outer frame
        draw.rectangle([0, 0, width - 1, height - 1], outline='#e0e0e0', width=1)

        # Font
        title_font = EnhancedChartRenderer._load_font(16, bold=True)
        label_font = EnhancedChartRenderer._load_font(12)

        if title:
            tb = draw.textbbox((0, 0), title, font=title_font)
            draw.text(((width - (tb[2] - tb[0])) / 2, 8), title, fill="#333", font=title_font)

        categories = data.get("categories", []) or []
        series_list = data.get("series", []) or []

        # Dispatch by type
        ct = chart_type or "bar"
        try:
            if ct in ("bar", "barGroup"):
                EnhancedChartRenderer._draw_bar_chart(draw, categories, series_list, width, height, label_font, options)
            elif ct in ("barStacked", "barStacked100"):
                EnhancedChartRenderer._draw_bar_stacked_chart(draw, categories, series_list, width, height, label_font,
                                                              percent=(ct == "barStacked100"))
            elif ct in ("barHorizontal",):
                EnhancedChartRenderer._draw_bar_horizontal_chart(draw, categories, series_list, width, height,
                                                                 label_font)
            elif ct in ("line", "lineSmooth"):
                EnhancedChartRenderer._draw_line_chart(draw, categories, series_list, width, height, label_font,
                                                       smooth=(ct == "lineSmooth"))
            elif ct == "pie":
                EnhancedChartRenderer._draw_pie_chart(draw, categories, series_list, width, height, label_font)
            elif ct == "doughnut":
                EnhancedChartRenderer._draw_doughnut_chart(draw, categories, series_list, width, height, label_font)
            elif ct in ("area", "areaStacked"):
                EnhancedChartRenderer._draw_area_chart(draw, categories, series_list, width, height, label_font,
                                                       stacked=(ct == "areaStacked"))
            elif ct == "scatter":
                EnhancedChartRenderer._draw_scatter_chart(draw, categories, series_list, width, height, label_font)
            elif ct == "bubble":
                EnhancedChartRenderer._draw_bubble_chart(draw, categories, series_list, width, height, label_font)
            elif ct == "radar":
                EnhancedChartRenderer._draw_radar_chart(draw, categories, series_list, width, height, label_font)
            else:
                draw.text((width / 2 - 50, height / 2 - 10), f"{ct.upper()}\nCHART", fill="#666", font=title_font,
                          align="center")
        except Exception as e:
            draw.text((10, height / 2), f"Preview failed: {e}", fill="red", font=label_font)

        # Draw legend
        if options and options.get("legend", True):
            EnhancedChartRenderer._draw_legend(draw, series_list, width, height, label_font)

        return img

    @staticmethod
    def _draw_bar_chart(draw, categories, series_list, width, height, font, options=None):
        """Draw bar chart"""
        legend_h = 40 if options and options.get("legend", True) else 20
        margin_x = max(30, int(width * 0.06))
        margin_y_top = max(30, int(height * 0.12))
        margin_y_bottom = max(38, int(height * 0.18))
        top, bottom = margin_y_top, height - margin_y_bottom
        left, right = margin_x, width - margin_x

        if not categories or not series_list:
            return

        cat_count = len(categories)
        series_count = len(series_list)
        plot_w = max(1, (right - left))
        group_w = plot_w / cat_count

        inner_gap_ratio = 0.2 if series_count > 1 else 0.35
        inner_gap = inner_gap_ratio * group_w
        bar_w = (group_w - inner_gap) / max(1, series_count)

        max_val = max((max(s.get("values", [0])) for s in series_list), default=0)
        if max_val <= 0:
            max_val = 1

        # Draw grid lines
        grid_lines = 5
        for i in range(grid_lines + 1):
            ratio = i / grid_lines
            y = bottom - ratio * (bottom - top)
            val = int(max_val * ratio)
            if 0 < i < grid_lines:
                draw.line([left, y, right, y], fill="#e5e5e5", width=1)
            label = str(val)
            tw, th = draw.textbbox((0, 0), label, font=font)[2:4]
            draw.text((left - tw - 6, y - th / 2), label, fill="#444", font=font)

        # Draw bars
        for ci in range(cat_count):
            base_x = left + ci * group_w + inner_gap / 2
            for si, s in enumerate(series_list):
                vals = s.get("values", [])
                if ci >= len(vals):
                    continue
                v = vals[ci]
                color = s.get("color", CHART_COLORS[si % len(CHART_COLORS)])
                h = (v / max_val) * (bottom - top)
                x0 = base_x + si * bar_w
                y0 = bottom - h

                # Support gradient
                gradient = s.get("gradient")
                if gradient:
                    # Simple gradient simulation
                    stops = gradient.get("stops", [])
                    if len(stops) >= 2:
                        color = stops[0].get("color", color)

                draw.rectangle([x0, y0, x0 + bar_w * 0.9, bottom], fill=color, outline=color)

                # Data labels
                if options and options.get("dataLabels", False):
                    draw.text((x0, y0 - 14), str(v), fill="#444", font=font)

        # Category label
        for ci, cat in enumerate(categories):
            cx = left + ci * group_w + group_w / 2
            label = str(cat)
            tb = draw.textbbox((0, 0), label, font=font)
            tw = tb[2] - tb[0]
            draw.text((cx - tw / 2, bottom + 6), label, fill="#333", font=font)

    @staticmethod
    def _draw_bar_horizontal_chart(draw, categories, series_list, width, height, font):
        """Draw horizontal bar chart"""
        margin = 50
        legend_h = 40
        top, bottom = margin, height - margin - legend_h
        left, right = margin + 40, width - margin

        if not categories or not series_list:
            return

        cat_count = len(categories)
        series_count = len(series_list)
        plot_h = bottom - top
        group_h = plot_h / cat_count
        bar_h = group_h / (series_count + 1)

        max_val = max((max(s.get("values", [0])) for s in series_list), default=0) or 1

        # Draw axes
        draw.line([left, top, left, bottom], fill="#555", width=1)
        draw.line([left, bottom, right, bottom], fill="#555", width=1)

        # Draw bars
        for ci, cat in enumerate(categories):
            base_y = top + ci * group_h

            # Category label
            draw.text((left - 40, base_y + group_h / 2 - 5), str(cat)[:8], fill="#333", font=font)

            for si, s in enumerate(series_list):
                vals = s.get("values", [])
                if ci >= len(vals):
                    continue
                v = vals[ci]
                color = s.get("color", CHART_COLORS[si % len(CHART_COLORS)])
                w = (v / max_val) * (right - left)
                y0 = base_y + si * bar_h + bar_h * 0.1
                draw.rectangle([left, y0, left + w, y0 + bar_h * 0.8], fill=color, outline=color)

    @staticmethod
    def _draw_doughnut_chart(draw, categories, series_list, width, height, font):
        """Draw donut chart"""
        if not series_list or not categories:
            return
        vals = series_list[0].get("values", [])
        total = sum(vals) or 1
        cx, cy = width // 2, height // 2
        outer_radius = min(width, height) // 3
        inner_radius = outer_radius // 2

        start = 0
        for i, v in enumerate(vals[:len(categories)]):
            angle = v / total * 360
            color = series_list[0].get("color") or CHART_COLORS[i % len(CHART_COLORS)]

            # Outer circle
            draw.pieslice([cx - outer_radius, cy - outer_radius, cx + outer_radius, cy + outer_radius],
                          start=start, end=start + angle, fill=color, outline="white")
            start += angle

        # Inner circle (hollow)
        draw.ellipse([cx - inner_radius, cy - inner_radius, cx + inner_radius, cy + inner_radius],
                     fill="white", outline="white")

    @staticmethod
    def _draw_radar_chart(draw, categories, series_list, width, height, font):
        """Draw radar chart"""
        cx, cy = width // 2, height // 2
        radius = min(width, height) // 3
        n = len(categories)
        if n < 3:
            return

        # Draw grid
        for r in [radius * 0.2, radius * 0.4, radius * 0.6, radius * 0.8, radius]:
            points = []
            for i in range(n):
                angle = 2 * math.pi * i / n - math.pi / 2
                x = cx + r * math.cos(angle)
                y = cy + r * math.sin(angle)
                points.append((x, y))

            # Draw polygon grid
            for i in range(n):
                draw.line([points[i], points[(i + 1) % n]], fill="#e0e0e0", width=1)

        # Draw axes and labels
        for i, cat in enumerate(categories):
            angle = 2 * math.pi * i / n - math.pi / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            draw.line([(cx, cy), (x, y)], fill="#d0d0d0", width=1)

            # Labels
            label_x = cx + (radius + 20) * math.cos(angle)
            label_y = cy + (radius + 20) * math.sin(angle)
            draw.text((label_x - 20, label_y - 5), str(cat)[:8], fill="#333", font=font)

        # Draw data
        for si, s in enumerate(series_list):
            vals = s.get("values", [])
            max_val = max(vals) if vals else 1
            color = s.get("color", CHART_COLORS[si % len(CHART_COLORS)])

            points = []
            for i in range(min(n, len(vals))):
                v = vals[i] / max_val
                angle = 2 * math.pi * i / n - math.pi / 2
                x = cx + radius * v * math.cos(angle)
                y = cy + radius * v * math.sin(angle)
                points.append((x, y))

            if len(points) >= 3:
                # Transparent fill
                img_temp = Image.new('RGBA', (width, height), (255, 255, 255, 0))
                draw_temp = ImageDraw.Draw(img_temp)
                r, g, b = hex_to_rgb(color)[:3]
                draw_temp.polygon(points, fill=(r, g, b, 80), outline=color)
                draw.bitmap((0, 0), img_temp, fill=None)

                # Draw border
                for i in range(len(points)):
                    draw.line([points[i], points[(i + 1) % len(points)]], fill=color, width=2)

    @staticmethod
    def _draw_bubble_chart(draw, categories, series_list, width, height, font):
        """Draw bubble chart"""
        margin = 50
        top, bottom = margin, height - margin - 40
        left, right = margin, width - margin

        if not series_list:
            return

        # Draw axes
        draw.line([left, bottom, right, bottom], fill="#555", width=1)
        draw.line([left, top, left, bottom], fill="#555", width=1)

        # Collect all data points
        all_points = []
        for si, s in enumerate(series_list):
            color = s.get("color", CHART_COLORS[si % len(CHART_COLORS)])
            for val in s.get("values", []):
                if isinstance(val, dict):
                    x = val.get("x", 0)
                    y = val.get("y", 0)
                    size = val.get("size", 10)
                    all_points.append((x, y, size, color))

        if not all_points:
            return

        # Calculate range
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        if max_x == min_x: max_x += 1
        if max_y == min_y: max_y += 1

        # Draw bubbles
        for x, y, size, color in all_points:
            px = left + (x - min_x) / (max_x - min_x) * (right - left)
            py = bottom - (y - min_y) / (max_y - min_y) * (bottom - top)
            r = size / 2

            # Transparent bubble
            img_temp = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw_temp = ImageDraw.Draw(img_temp)
            rgb = hex_to_rgb(color)[:3]
            draw_temp.ellipse([px - r, py - r, px + r, py + r], fill=(*rgb, 120), outline=color)
            draw.bitmap((0, 0), img_temp, fill=None)

    @staticmethod
    def _draw_pie_chart(draw, categories, series_list, width, height, font):
        if not series_list or not categories:
            return
        vals = series_list[0].get("values", [])
        total = sum(vals) or 1
        cx, cy = width // 2, height // 2
        radius = min(width, height) // 3
        start = 0
        for i, v in enumerate(vals[:len(categories)]):
            angle = v / total * 360
            color = series_list[0].get("color") or CHART_COLORS[i % len(CHART_COLORS)]
            draw.pieslice([cx - radius, cy - radius, cx + radius, cy + radius], start=start, end=start + angle,
                          fill=color, outline="white")
            mid = start + angle / 2
            lx = cx + int(radius * 0.6 * math.cos(math.radians(mid)))
            ly = cy + int(radius * 0.6 * math.sin(math.radians(mid)))
            pct = f"{(v / total) * 100:.1f}%"
            draw.text((lx - 15, ly - 7), pct, fill="white", font=font)
            start += angle

    @staticmethod
    def _draw_line_chart(draw, categories, series_list, width, height, font, smooth=False):
        margin = 50
        legend_h = 40
        top, bottom = margin, height - margin - legend_h
        left, right = margin, width - margin
        if not categories or not series_list:
            return
        max_v = max((max(s.get("values", [0])) for s in series_list), default=0) or 1

        # Axes
        draw.line([left, bottom, right, bottom], fill="#555", width=1)
        draw.line([left, top, left, bottom], fill="#555", width=1)

        # Grid lines
        for i in range(5):
            y = top + (bottom - top) * i / 4
            draw.line([left, y, right, y], fill="#e5e5e5", width=1)

        # X-axis labels
        step = (right - left) / (len(categories) - 1 if len(categories) > 1 else 1)
        for i, cat in enumerate(categories):
            x = left + i * step
            draw.text((x - 15, bottom + 5), str(cat)[:6], fill="#333", font=font)

        # Draw lines
        for si, s in enumerate(series_list):
            color = s.get("color", CHART_COLORS[si % len(CHART_COLORS)])
            pts = []
            for ci, v in enumerate(s.get("values", [])[:len(categories)]):
                x = left + ci * step
                y = bottom - (v / max_v) * (bottom - top)
                pts.append((x, y))

            # Draw line
            for i in range(len(pts) - 1):
                draw.line([pts[i], pts[i + 1]], fill=color, width=2)

            # Draw points
            for x, y in pts:
                draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=color, outline=color)

    @staticmethod
    def _draw_bar_stacked_chart(draw, categories, series_list, width, height, font, percent=False):
        margin = 50
        legend_h = 40
        top, bottom = margin, height - margin - legend_h
        left, right = margin, width - margin
        if not categories or not series_list:
            return

        bar_w = (right - left) / (len(categories) * 1.25)
        gap = bar_w * 0.25

        totals = []
        for ci in range(len(categories)):
            t = 0
            for s in series_list:
                vals = s.get("values", [])
                if ci < len(vals):
                    t += vals[ci]
            totals.append(t or 1)

        max_total = max(totals) or 1

        for ci, cat in enumerate(categories):
            x0 = left + ci * (bar_w + gap)
            y_bottom = bottom

            for si, s in enumerate(series_list):
                vals = s.get("values", [])
                if ci >= len(vals):
                    continue
                v = vals[ci]

                if percent:
                    ratio = v / totals[ci] if totals[ci] else 0
                    h = ratio * (bottom - top)
                else:
                    h = (v / max_total) * (bottom - top)

                color = s.get("color", CHART_COLORS[si % len(CHART_COLORS)])
                y_top = y_bottom - h
                draw.rectangle([x0, y_top, x0 + bar_w, y_bottom], fill=color, outline=color)
                y_bottom = y_top

            # X-axis labels
            draw.text((x0, bottom + 5), str(cat)[:6], fill="#333", font=font)

    @staticmethod
    def _draw_area_chart(draw, categories, series_list, width, height, font, stacked=False):
        margin = 50
        legend_h = 40
        top, bottom = margin, height - margin - legend_h
        left, right = margin, width - margin
        if not categories or not series_list:
            return

        if stacked:
            max_v = 0
            for ci in range(len(categories)):
                max_v = max(max_v, sum(
                    (s.get("values", [0])[ci] if ci < len(s.get("values", [])) else 0) for s in series_list))
        else:
            max_v = max((max(s.get("values", [0])) for s in series_list), default=0)
        max_v = max_v or 1

        # Axes
        draw.line([left, bottom, right, bottom], fill="#555", width=1)
        draw.line([left, top, left, bottom], fill="#555", width=1)

        step = (right - left) / (len(categories) - 1 if len(categories) > 1 else 1)
        base = [0] * len(categories)

        for si, s in enumerate(series_list):
            color = s.get("color", CHART_COLORS[si % len(CHART_COLORS)])
            vals = s.get("values", [])
            line_pts = []
            poly = []

            for ci in range(len(categories)):
                v = vals[ci] if ci < len(vals) else 0
                acc = base[ci] + v if stacked else v
                x = left + ci * step
                y = bottom - (acc / max_v) * (bottom - top)
                line_pts.append((x, y))
                poly.append((x, y))

            # Close area
            if stacked:
                for ci in reversed(range(len(categories))):
                    x = left + ci * step
                    y = bottom - (base[ci] / max_v) * (bottom - top)
                    poly.append((x, y))
            else:
                poly.extend([(right, bottom), (left, bottom)])

            # Transparent fill
            img_temp = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw_temp = ImageDraw.Draw(img_temp)
            r, g, b = hex_to_rgb(color)[:3]
            draw_temp.polygon(poly, fill=(r, g, b, 80))
            draw.bitmap((0, 0), img_temp, fill=None)

            # Draw lines
            for i in range(len(line_pts) - 1):
                draw.line([line_pts[i], line_pts[i + 1]], fill=color, width=2)

            if stacked:
                for ci in range(len(categories)):
                    v = vals[ci] if ci < len(vals) else 0
                    base[ci] += v

    @staticmethod
    def _draw_scatter_chart(draw, categories, series_list, width, height, font):
        margin = 50
        legend_h = 40
        top, bottom = margin, height - margin - legend_h
        left, right = margin, width - margin
        if not series_list:
            return

        # Axes
        draw.line([left, bottom, right, bottom], fill="#555", width=1)
        draw.line([left, top, left, bottom], fill="#555", width=1)

        points = []
        for s in series_list:
            for itm in s.get("values", []):
                if isinstance(itm, (list, tuple)) and len(itm) >= 2:
                    points.append((float(itm[0]), float(itm[1])))
                elif isinstance(itm, dict) and 'x' in itm and 'y' in itm:
                    points.append((float(itm['x']), float(itm['y'])))

        if not points:
            return

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        if max_x - min_x == 0: max_x += 1
        if max_y - min_y == 0: max_y += 1

        for si, s in enumerate(series_list):
            color = s.get("color", CHART_COLORS[si % len(CHART_COLORS)])
            for itm in s.get("values", []):
                if isinstance(itm, (list, tuple)) and len(itm) >= 2:
                    x_val, y_val = itm[0], itm[1]
                elif isinstance(itm, dict) and 'x' in itm and 'y' in itm:
                    x_val, y_val = itm['x'], itm['y']
                else:
                    continue

                x = left + (float(x_val) - min_x) / (max_x - min_x) * (right - left)
                y = bottom - (float(y_val) - min_y) / (max_y - min_y) * (bottom - top)
                draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=color, outline=color)

    @staticmethod
    def _draw_legend(draw, series_list, width, height, font):
        if not series_list:
            return
        base_y = height - 30
        x = 10
        for i, s in enumerate(series_list[:8]):
            color = s.get("color", CHART_COLORS[i % len(CHART_COLORS)])
            name = (s.get("name") or f"S{i + 1}")[:10]
            draw.rectangle([x, base_y, x + 14, base_y + 14], fill=color, outline=color)
            draw.text((x + 18, base_y - 1), name, fill="#222", font=font)
            x += 90


class PPTPreview(ttk.Frame):
    """Enhanced PPT preview component"""

    def __init__(self, master: tk.Widget):
        super().__init__(master)

        self.preview_container = ttk.Frame(self, style="Preview.TFrame")
        self.preview_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.canvas = tk.Canvas(
            self.preview_container,
            bg=COLOR_CANVAS_BG,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            relief=tk.SOLID,
            bd=1
        )
        self.canvas.pack(expand=True)

        self.slide_images: List[ImageTk.PhotoImage] = []
        self.current_slide_index = 0
        self.slides: List[Dict[str, Any]] = []
        self.slide_size = (DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.current_meta: Optional[Dict[str, Any]] = None
        self.scale = 1.0
        self.chart_renderer = EnhancedChartRenderer()
        self.theme = {}  # Theme configuration

    def set_meta(self, meta: Dict[str, Any]):
        """Set PPT metadata"""
        ppt_cfg = meta.get("ppt", {})
        size_cfg = ppt_cfg.get("size", {})
        width = float(size_cfg.get("width", DEFAULT_WIDTH))
        height = float(size_cfg.get("height", DEFAULT_HEIGHT))
        self.slide_size = (width, height)
        self.slides = ppt_cfg.get("slides", [])
        self.current_slide_index = max(0, min(self.current_slide_index, len(self.slides) - 1))
        self.current_meta = meta
        self.theme = ppt_cfg.get("theme", {})

        self.scale = min(PREVIEW_MAX_WIDTH / width, PREVIEW_MAX_HEIGHT / height, 1.0)

        logger.info(
            "Preview Settings: slides=%s, current index=%s, size=%s, zoom=%s",
            len(self.slides),
            self.current_slide_index,
            self.slide_size,
            self.scale,
        )
        self.render()

    def resolve_color(self, color: str) -> str:
        """Parse color values, supports theme variables"""
        if not color:
            return "#000000"

        if color.startswith('$'):
            var_name = color[1:]
            if self.theme and 'colors' in self.theme:
                return self.theme['colors'].get(var_name, color)

        return color

    @staticmethod
    def _resolve_box_px(box: Dict[str, Any], slide_w: float, slide_h: float, default_unit: str):
        unit = box.get("unit", default_unit or "px")

        def to_px(value: float, total: float) -> float:
            if value is None:
                return 0.0
            if unit == "percent":
                return total * float(value) / 100.0
            return float(value)

        width = to_px(box.get("w", slide_w), slide_w)
        height = to_px(box.get("h", slide_h), slide_h)
        return (
            to_px(box.get("x", 0), slide_w),
            to_px(box.get("y", 0), slide_h),
            width,
            height,
        )

    def create_gradient_image(self, width: int, height: int, gradient_cfg: Dict[str, Any]) -> Image.Image:
        """Create gradient image"""
        img = Image.new('RGBA', (width, height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        gradient_type = gradient_cfg.get("type", "linear")
        stops = gradient_cfg.get("stops", [])

        if not stops or len(stops) < 2:
            return img

        if gradient_type == "linear":
            angle = gradient_cfg.get("angle", 0)

            # Simplified implementation: horizontal or vertical gradient
            for y in range(height):
                ratio = y / height

                # Find corresponding color range
                color = None
                for i in range(len(stops) - 1):
                    stop1 = stops[i]
                    stop2 = stops[i + 1]
                    pos1 = stop1.get("position", 0) / 100
                    pos2 = stop2.get("position", 100) / 100

                    if pos1 <= ratio <= pos2:
                        # Interpolate between two stops
                        local_ratio = (ratio - pos1) / (pos2 - pos1) if pos2 > pos1 else 0
                        color1 = hex_to_rgb(self.resolve_color(stop1.get("color", "#000000")))[:3]
                        color2 = hex_to_rgb(self.resolve_color(stop2.get("color", "#ffffff")))[:3]

                        r = int(color1[0] + (color2[0] - color1[0]) * local_ratio)
                        g = int(color1[1] + (color2[1] - color1[1]) * local_ratio)
                        b = int(color1[2] + (color2[2] - color1[2]) * local_ratio)
                        color = (r, g, b)
                        break

                if color:
                    draw.line([(0, y), (width, y)], fill=color)

        elif gradient_type == "radial":
            # Radial gradient (simplified implementation)
            cx, cy = width // 2, height // 2
            max_radius = math.sqrt(cx ** 2 + cy ** 2)

            for r in range(int(max_radius)):
                ratio = r / max_radius

                # Find corresponding color
                color = None
                for i in range(len(stops) - 1):
                    stop1 = stops[i]
                    stop2 = stops[i + 1]
                    pos1 = stop1.get("position", 0) / 100
                    pos2 = stop2.get("position", 100) / 100

                    if pos1 <= ratio <= pos2:
                        local_ratio = (ratio - pos1) / (pos2 - pos1) if pos2 > pos1 else 0
                        color1 = hex_to_rgb(self.resolve_color(stop1.get("color", "#000000")))[:3]
                        color2 = hex_to_rgb(self.resolve_color(stop2.get("color", "#ffffff")))[:3]

                        red = int(color1[0] + (color2[0] - color1[0]) * local_ratio)
                        green = int(color1[1] + (color2[1] - color1[1]) * local_ratio)
                        blue = int(color1[2] + (color2[2] - color1[2]) * local_ratio)
                        color = (red, green, blue)
                        break

                if color:
                    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color)

        return img

    def apply_shadow(self, img: Image.Image, shadow_cfg: Dict[str, Any]) -> Image.Image:
        """Apply shadow effect"""
        if not shadow_cfg:
            return img

        x_offset = int(shadow_cfg.get("x", 2) * self.scale)
        y_offset = int(shadow_cfg.get("y", 2) * self.scale)
        blur = shadow_cfg.get("blur", 4)
        color = hex_to_rgb(self.resolve_color(shadow_cfg.get("color", "#00000040")))[:4]

        # Create shadow layer
        shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
        shadow.paste((color[0], color[1], color[2], color[3] if len(color) > 3 else 128),
                     [0, 0, img.width, img.height])

        # Apply blur
        if blur > 0:
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))

        # Composite
        final = Image.new('RGBA',
                          (img.width + abs(x_offset), img.height + abs(y_offset)),
                          (0, 0, 0, 0))
        final.paste(shadow, (max(0, x_offset), max(0, y_offset)))
        final.paste(img, (max(0, -x_offset), max(0, -y_offset)), img)

        return final

    def render_background(self, slide_cfg: Dict[str, Any]):
        """Render background, supports gradient"""
        self.canvas.delete("background")
        sw, sh = self.slide_size
        scaled_w = int(sw * self.scale)
        scaled_h = int(sh * self.scale)

        bg_cfg = slide_cfg.get("background", {}) if slide_cfg else {}

        # Prefer gradient, otherwise solid color
        gradient = bg_cfg.get("gradient")
        if gradient:
            gradient_img = self.create_gradient_image(scaled_w, scaled_h, gradient)
            photo = ImageTk.PhotoImage(gradient_img)
            self.slide_images.append(photo)
            self.canvas.create_image(0, 0, anchor="nw", image=photo, tags="background")
        else:
            color = self.resolve_color(bg_cfg.get("color", "#ffffff"))
            self.canvas.create_rectangle(
                0, 0, scaled_w, scaled_h,
                fill=color, outline="", tags="background"
            )

        # Background image
        img_cfg = bg_cfg.get("image") if isinstance(bg_cfg, dict) else None
        if img_cfg and isinstance(img_cfg, dict):
            content = get_image_bytes(img_cfg.get("src"), logger)
            if content:
                try:
                    image = Image.open(BytesIO(content))
                    image = image.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)

                    # Apply transparency
                    if "opacity" in img_cfg:
                        opacity = img_cfg["opacity"]
                        if 0 <= opacity < 1:
                            image = image.convert("RGBA")
                            alpha = image.split()[-1]
                            alpha = alpha.point(lambda p: p * opacity)
                            image.putalpha(alpha)

                    # Apply filter
                    filter_type = img_cfg.get("filter")
                    if filter_type == "blur":
                        blur_val = img_cfg.get("blur", 5)
                        image = image.filter(ImageFilter.GaussianBlur(radius=blur_val))
                    elif filter_type == "grayscale":
                        image = ImageOps.grayscale(image)

                    photo = ImageTk.PhotoImage(image=image)
                    self.slide_images.append(photo)
                    self.canvas.create_image(0, 0, anchor="nw", image=photo, tags="background")
                except Exception as exc:
                    logger.warning("Background image rendering failed: %s", exc)

    def draw_text(self, elem: Dict[str, Any], default_unit: str):
        """Draw text, supports shadow and rotation"""
        slide_w, slide_h = self.slide_size
        x, y, width, height = self._resolve_box_px(elem.get("box", {}), slide_w, slide_h, default_unit)

        x *= self.scale
        y *= self.scale
        width *= self.scale
        height *= self.scale

        text = elem.get("text", "")
        style = elem.get("style", {})

        # Handle paragraphs
        paragraphs = elem.get("paragraphs")
        if paragraphs:
            texts = []
            for para in paragraphs:
                para_text = para.get("text", "")
                list_type = para.get("listType")
                if list_type == "bullet":
                    bullet_char = para.get("bulletChar", "•")
                    para_text = f"{bullet_char} {para_text}"
                elif list_type == "number":
                    number = para.get("number", len(texts) + 1)
                    prefix = para.get("numberPrefix", "")
                    para_text = f"{prefix}{number}. {para_text}"
                texts.append(para_text)
            text = "\n".join(texts)

        font_size = int(style.get("fontSize", 32) * self.scale * 0.75)
        font_family = style.get("fontFamily", "Microsoft YaHei")

        # Support theme fonts
        if font_family.startswith('$'):
            if self.theme and 'fonts' in self.theme:
                if font_family == '$heading':
                    font_family = self.theme['fonts'].get('heading', 'Arial')
                elif font_family == '$body':
                    font_family = self.theme['fonts'].get('body', 'Arial')

        fill = self.resolve_color(style.get("color", "#000000"))
        align = style.get("align", "left")
        bold = style.get("bold", False)
        italic = style.get("italic", False)

        font_style = []
        if bold:
            font_style.append("bold")
        if italic:
            font_style.append("italic")
        font_tuple = (font_family, max(8, font_size), " ".join(font_style) if font_style else "normal")

        # Background color
        if elem.get("fill"):
            self.canvas.create_rectangle(
                x, y, x + width, y + height,
                fill=self.resolve_color(elem["fill"]),
                outline="",
                tags="element"
            )

        # Border
        if elem.get("border"):
            self.draw_border(x, y, width, height, elem["border"])

        if align == "center":
            anchor = "n"
            text_x = x + width / 2
        elif align == "right":
            anchor = "ne"
            text_x = x + width
        else:
            anchor = "nw"
            text_x = x

        # Text shadow
        shadow = elem.get("shadow") or style.get("textShadow")
        if shadow:
            shadow_x = shadow.get("x", 2) * self.scale
            shadow_y = shadow.get("y", 2) * self.scale
            shadow_color = self.resolve_color(shadow.get("color", "#00000040"))
            self.canvas.create_text(
                text_x + shadow_x, y + shadow_y,
                text=text,
                font=font_tuple,
                fill=shadow_color,
                anchor=anchor,
                width=width,
                tags="element",
                justify={"center": "center", "right": "right"}.get(align, "left")
            )

        # Main text
        text_item = self.canvas.create_text(
            text_x, y,
            text=text,
            font=font_tuple,
            fill=fill,
            anchor=anchor,
            width=width,
            tags="element",
            justify={"center": "center", "right": "right"}.get(align, "left")
        )

        # Rotation
        if "rotation" in elem:
            self.apply_rotation(text_item, elem["rotation"], x + width / 2, y + height / 2)

    def draw_border(self, x: float, y: float, width: float, height: float, border_cfg: Dict[str, Any]):
        """Draw border"""
        if not border_cfg:
            return

        border_width = border_cfg.get("width", 1)
        border_color = self.resolve_color(border_cfg.get("color", "#000000"))
        border_style = border_cfg.get("style", "solid")

        dash_pattern = None
        if border_style == "dashed":
            dash_pattern = (5, 2)
        elif border_style == "dotted":
            dash_pattern = (2, 2)

        self.canvas.create_rectangle(
            x, y, x + width, y + height,
            outline=border_color,
            width=border_width,
            dash=dash_pattern,
            fill="",
            tags="element"
        )

    def apply_rotation(self, item_id, angle: float, cx: float, cy: float):
        """Apply rotation (simplified implementation)"""
        # Canvas does not directly support rotation, just as a mark
        pass

    def draw_shape(self, elem: Dict[str, Any], default_unit: str):
        """Draw shapes, supports more types"""
        slide_w, slide_h = self.slide_size
        x, y, width, height = self._resolve_box_px(elem.get("box", {}), slide_w, slide_h, default_unit)

        x *= self.scale
        y *= self.scale
        width *= self.scale
        height *= self.scale

        shape_type = elem.get("shapeType", "rect")
        fill = self.resolve_color(elem.get("fill", "#d1d5db"))

        # Gradient fill
        gradient = elem.get("gradient")
        if gradient:
            gradient_img = self.create_gradient_image(int(width), int(height), gradient)
            photo = ImageTk.PhotoImage(gradient_img)
            self.slide_images.append(photo)
            self.canvas.create_image(x, y, anchor="nw", image=photo, tags="element")

            # Border
            if elem.get("border"):
                self.draw_border(x, y, width, height, elem["border"])
            return

        # Shadow
        shadow = elem.get("shadow")
        if shadow:
            shadow_x = shadow.get("x", 2) * self.scale
            shadow_y = shadow.get("y", 2) * self.scale
            shadow_blur = shadow.get("blur", 4)
            shadow_color = self.resolve_color(shadow.get("color", "#00000030"))

            # Draw shadow shape
            self._draw_shape_primitive(
                x + shadow_x, y + shadow_y, width, height,
                shape_type, shadow_color, None, "shadow"
            )

        # Main shape
        shape_id = self._draw_shape_primitive(x, y, width, height, shape_type, fill, elem.get("border"), "element")

        # Rotation
        if "rotation" in elem and shape_id:
            self.apply_rotation(shape_id, elem["rotation"], x + width / 2, y + height / 2)

    def _draw_shape_primitive(self, x: float, y: float, width: float, height: float,
                              shape_type: str, fill: str, border: Optional[Dict], tags: str):
        """Draw basic shapes"""
        if shape_type in ["ellipse", "circle"]:
            if shape_type == "circle":
                size = min(width, height)
                width = height = size
            return self.canvas.create_oval(
                x, y, x + width, y + height,
                fill=fill, outline="", tags=tags
            )
        elif shape_type == "triangle":
            points = [x + width / 2, y, x, y + height, x + width, y + height]
            return self.canvas.create_polygon(points, fill=fill, outline="", tags=tags)
        elif shape_type == "star" or shape_type.startswith("star"):
            # Pentagon star
            cx, cy = x + width / 2, y + height / 2
            outer_r = min(width, height) / 2
            inner_r = outer_r * 0.4
            points = []
            n = 5  # Default pentagon star
            if shape_type == "star6":
                n = 6
            elif shape_type == "star8":
                n = 8

            for i in range(n * 2):
                angle = math.pi * i / n - math.pi / 2
                r = outer_r if i % 2 == 0 else inner_r
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle)
                points.extend([px, py])

            return self.canvas.create_polygon(points, fill=fill, outline="", tags=tags)
        elif shape_type == "hexagon":
            cx, cy = x + width / 2, y + height / 2
            r = min(width, height) / 2
            points = []
            for i in range(6):
                angle = math.pi * i / 3
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle)
                points.extend([px, py])
            return self.canvas.create_polygon(points, fill=fill, outline="", tags=tags)
        elif shape_type == "diamond":
            points = [x + width / 2, y, x + width, y + height / 2, x + width / 2, y + height, x, y + height / 2]
            return self.canvas.create_polygon(points, fill=fill, outline="", tags=tags)
        elif shape_type in ["arrow", "arrowRight"]:
            points = [x, y + height * 0.3, x + width * 0.6, y + height * 0.3,
                      x + width * 0.6, y, x + width, y + height / 2,
                      x + width * 0.6, y + height, x + width * 0.6, y + height * 0.7,
                      x, y + height * 0.7]
            return self.canvas.create_polygon(points, fill=fill, outline="", tags=tags)
        elif shape_type == "heart":
            # Simplified heart shape
            points = []
            for t in range(0, 360, 10):
                rad = math.radians(t)
                px = 16 * math.sin(rad) ** 3
                py = -(13 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad))
                points.extend([x + width / 2 + px * width / 32, y + height / 2 + py * height / 32])
            return self.canvas.create_polygon(points, fill=fill, outline="", tags=tags, smooth=True)
        elif shape_type == "plus":
            # Cross
            w3 = width / 3
            h3 = height / 3
            points = [
                x + w3, y, x + 2 * w3, y, x + 2 * w3, y + h3,
                x + width, y + h3, x + width, y + 2 * h3,
                x + 2 * w3, y + 2 * h3, x + 2 * w3, y + height,
                x + w3, y + height, x + w3, y + 2 * h3,
                x, y + 2 * h3, x, y + h3, x + w3, y + h3
            ]
            return self.canvas.create_polygon(points, fill=fill, outline="", tags=tags)
        else:
            # Default rectangle
            shape_id = self.canvas.create_rectangle(
                x, y, x + width, y + height,
                fill=fill, outline="", tags=tags
            )

            # Border
            if border:
                self.draw_border(x, y, width, height, border)

            return shape_id

    def draw_line(self, elem: Dict[str, Any], default_unit: str):
        """Draw line element"""
        slide_w, slide_h = self.slide_size
        points = elem.get("points", [])

        if len(points) < 2:
            return

        stroke = self.resolve_color(elem.get("stroke", "#000000"))
        stroke_width = elem.get("strokeWidth", 1) * self.scale
        stroke_style = elem.get("strokeStyle", "solid")

        dash_pattern = None
        if stroke_style == "dashed":
            dash_pattern = (5, 2)
        elif stroke_style == "dotted":
            dash_pattern = (2, 2)

        # Convert point coordinates
        converted_points = []
        for point in points:
            px = point.get("x", 0) * self.scale
            py = point.get("y", 0) * self.scale
            converted_points.extend([px, py])

        # Draw lines
        if elem.get("curved"):
            self.canvas.create_line(
                converted_points,
                fill=stroke,
                width=stroke_width,
                dash=dash_pattern,
                smooth=True,
                tags="element"
            )
        else:
            self.canvas.create_line(
                converted_points,
                fill=stroke,
                width=stroke_width,
                dash=dash_pattern,
                tags="element"
            )

        # Arrow
        if len(points) >= 2:
            start_arrow = elem.get("startArrow", "none")
            end_arrow = elem.get("endArrow", "none")

            if end_arrow == "arrow":
                # Draw arrow
                p1 = points[-2]
                p2 = points[-1]
                self._draw_arrow_head(
                    p1.get("x", 0) * self.scale,
                    p1.get("y", 0) * self.scale,
                    p2.get("x", 0) * self.scale,
                    p2.get("y", 0) * self.scale,
                    stroke
                )

    def _draw_arrow_head(self, x1: float, y1: float, x2: float, y2: float, color: str):
        """Draw arrow head"""
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_length = 10 * self.scale
        arrow_angle = math.pi / 6

        # Calculate two arrow points
        x3 = x2 - arrow_length * math.cos(angle - arrow_angle)
        y3 = y2 - arrow_length * math.sin(angle - arrow_angle)
        x4 = x2 - arrow_length * math.cos(angle + arrow_angle)
        y4 = y2 - arrow_length * math.sin(angle + arrow_angle)

        self.canvas.create_polygon(
            [x2, y2, x3, y3, x4, y4],
            fill=color,
            outline=color,
            tags="element"
        )

    def draw_icon(self, elem: Dict[str, Any], default_unit: str):
        """Draw icon element"""
        slide_w, slide_h = self.slide_size
        x, y, width, height = self._resolve_box_px(elem.get("box", {}), slide_w, slide_h, default_unit)

        x *= self.scale
        y *= self.scale
        width *= self.scale
        height *= self.scale

        # Use shape to simulate icon
        color = self.resolve_color(elem.get("color", "#000000"))
        gradient = elem.get("gradient")

        if gradient:
            gradient_img = self.create_gradient_image(int(width), int(height), gradient)
            photo = ImageTk.PhotoImage(gradient_img)
            self.slide_images.append(photo)
            self.canvas.create_image(x, y, anchor="nw", image=photo, tags="element")
        else:
            # Draw a simple star as icon
            cx, cy = x + width / 2, y + height / 2
            r = min(width, height) / 2
            points = []
            for i in range(10):
                angle = math.pi * i / 5 - math.pi / 2
                radius = r if i % 2 == 0 else r * 0.5
                px = cx + radius * math.cos(angle)
                py = cy + radius * math.sin(angle)
                points.extend([px, py])

            self.canvas.create_polygon(points, fill=color, outline="", tags="element")

    def draw_group(self, elem: Dict[str, Any], default_unit: str):
        """Draw group element"""
        elements = elem.get("elements", [])

        # Recursively draw sub-elements
        for sub_elem in elements:
            self.draw_element(sub_elem, default_unit)

    def draw_video(self, elem: Dict[str, Any], default_unit: str):
        """Draw video placeholder"""
        slide_w, slide_h = self.slide_size
        x, y, width, height = self._resolve_box_px(elem.get("box", {}), slide_w, slide_h, default_unit)

        x *= self.scale
        y *= self.scale
        width *= self.scale
        height *= self.scale

        # Draw video placeholder
        self.canvas.create_rectangle(
            x, y, x + width, y + height,
            fill="#000000",
            outline=COLOR_BORDER,
            width=2,
            tags="element"
        )

        # Play button
        cx, cy = x + width / 2, y + height / 2
        r = min(width, height) / 8
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill="#ffffff",
            outline="",
            tags="element"
        )

        # Triangle play icon
        points = [
            cx - r * 0.3, cy - r * 0.5,
            cx - r * 0.3, cy + r * 0.5,
            cx + r * 0.5, cy
        ]
        self.canvas.create_polygon(points, fill="#000000", outline="", tags="element")

    def draw_smartart(self, elem: Dict[str, Any], default_unit: str):
        """Draw SmartArt"""
        slide_w, slide_h = self.slide_size
        x, y, width, height = self._resolve_box_px(elem.get("box", {}), slide_w, slide_h, default_unit)

        x *= self.scale
        y *= self.scale
        width *= self.scale
        height *= self.scale

        smartart_type = elem.get("smartArtType", "list")
        nodes = elem.get("nodes", [])

        if not nodes:
            return

        if smartart_type in ["list", "process"]:
            # List or flowchart
            node_width = width * 0.8 / len(nodes)
            node_height = height * 0.6

            for i, node in enumerate(nodes):
                node_x = x + i * (width / len(nodes)) + width * 0.1 / len(nodes)
                node_y = y + height * 0.2

                # Node color
                node_color = self.resolve_color(node.get("color", "#3B82F6"))

                # Draw node
                self.canvas.create_rectangle(
                    node_x, node_y,
                    node_x + node_width, node_y + node_height,
                    fill=node_color,
                    outline="",
                    tags="element"
                )

                # Node text
                text = node.get("text", f"Item {i + 1}")
                self.canvas.create_text(
                    node_x + node_width / 2,
                    node_y + node_height / 2,
                    text=text,
                    font=("Microsoft YaHei", max(10, int(14 * self.scale))),
                    fill="white",
                    anchor="center",
                    width=node_width * 0.9,
                    tags="element"
                )

                # Connection line
                if i < len(nodes) - 1:
                    self.canvas.create_line(
                        node_x + node_width, node_y + node_height / 2,
                        node_x + node_width + width * 0.1 / len(nodes), node_y + node_height / 2,
                        fill="#666666",
                        width=2,
                        arrow=tk.LAST,
                        tags="element"
                    )

        elif smartart_type == "cycle":
            # Circular diagram
            cx, cy = x + width / 2, y + height / 2
            radius = min(width, height) / 3

            for i, node in enumerate(nodes):
                angle = 2 * math.pi * i / len(nodes) - math.pi / 2
                node_x = cx + radius * math.cos(angle)
                node_y = cy + radius * math.sin(angle)

                node_color = self.resolve_color(node.get("color", CHART_COLORS[i % len(CHART_COLORS)]))

                # Draw node
                node_r = min(width, height) / 10
                self.canvas.create_oval(
                    node_x - node_r, node_y - node_r,
                    node_x + node_r, node_y + node_r,
                    fill=node_color,
                    outline="",
                    tags="element"
                )

                # Node text
                text = node.get("text", f"Item {i + 1}")
                self.canvas.create_text(
                    node_x, node_y,
                    text=text[:5],
                    font=("Microsoft YaHei", max(9, int(11 * self.scale))),
                    fill="white",
                    anchor="center",
                    tags="element"
                )

    def draw_image(self, elem: Dict[str, Any], default_unit: str):
        """Draw image, supports filters"""
        slide_w, slide_h = self.slide_size
        x, y, width, height = self._resolve_box_px(elem.get("box", {}), slide_w, slide_h, default_unit)

        x *= self.scale
        y *= self.scale
        width *= self.scale
        height *= self.scale

        content = get_image_bytes(elem.get("source"), logger)
        if not content:
            # Placeholder
            self.canvas.create_rectangle(
                x, y, x + width, y + height,
                outline=COLOR_BORDER, dash=(4, 2), width=2, tags="element"
            )
            self.canvas.create_text(
                x + width / 2, y + height / 2,
                text="🖼️ Image",
                font=("Microsoft YaHei", max(10, int(14 * self.scale))),
                fill=COLOR_TEXT_LIGHT,
                anchor="center",
                tags="element",
            )
            return

        try:
            img = Image.open(BytesIO(content))
            img = img.resize((int(width), int(height)), Image.Resampling.LANCZOS)

            # Apply filter
            filter_type = elem.get("filter")
            if filter_type == "grayscale":
                img = ImageOps.grayscale(img)
            elif filter_type == "sepia":
                # Simple sepia effect
                img = ImageOps.grayscale(img)
                img = ImageOps.colorize(img, '#704214', '#f0e68c')
            elif filter_type == "blur":
                filter_value = elem.get("filterValue", 5)
                img = img.filter(ImageFilter.GaussianBlur(radius=filter_value))

            photo = ImageTk.PhotoImage(image=img)
            self.slide_images.append(photo)
            self.canvas.create_image(x, y, anchor="nw", image=photo, tags="element")

            # Border
            if elem.get("border"):
                self.draw_border(x, y, width, height, elem["border"])

        except Exception as exc:
            logger.warning("Image rendering failed: %s", exc)

    def draw_chart(self, elem: Dict[str, Any], default_unit: str):
        """Render chart preview"""
        slide_w, slide_h = self.slide_size
        x, y, width, height = self._resolve_box_px(elem.get("box", {}), slide_w, slide_h, default_unit)

        x *= self.scale
        y *= self.scale
        width *= self.scale
        height *= self.scale

        chart_type = elem.get("chartType", "bar")
        title = elem.get("title", "")
        raw_data = elem.get("data", {}) or {}
        options = elem.get("chartOptions", {})

        # Alias compatibility -> internal actual rendering type
        alias_map = {
            "lineSmooth": "line",
            "barStacked": "bar",
            "barStacked100": "bar",
            "area": "line",          # Simulate with line + fill
            "areaStacked": "area",   # Delegate to internal logic (if supported), otherwise fallback
        }
        mapped_type = alias_map.get(chart_type, chart_type)
        chart_type = mapped_type

        # Deep copy and parse colors (supports theme variables like $primary), prevent PIL unknown color specifier
        try:
            data = copy.deepcopy(raw_data)
            series_list = data.get("series") or []
            for s in series_list:
                # Parse direct color
                if isinstance(s, dict) and s.get("color"):
                    s["color"] = self.resolve_color(s.get("color"))
                # Parse gradient color stops
                gradient = s.get("gradient") if isinstance(s, dict) else None
                if isinstance(gradient, dict):
                    stops = gradient.get("stops")
                    if isinstance(stops, list):
                        for stop in stops:
                            if isinstance(stop, dict) and stop.get("color"):
                                stop["color"] = self.resolve_color(stop.get("color"))
        except Exception as color_exc:
            logger.debug(f"chart color resolve skipped: {color_exc}")
            data = raw_data  # Fallback to original data (still try to render on failure)

        try:
            # Use enhanced chart renderer
            chart_img = self.chart_renderer.render_chart(
                chart_type, data, int(width), int(height), title, options
            )

            photo = ImageTk.PhotoImage(chart_img)
            self.slide_images.append(photo)
            self.canvas.create_image(x, y, anchor="nw", image=photo, tags="element")

        except Exception as e:
            logger.error(f"Chart rendering failed: {e}")
            # Show placeholder
            self.canvas.create_rectangle(
                x, y, x + width, y + height,
                fill="#f8f9fb", outline=COLOR_ACCENT, width=2, tags="element"
            )

            icon = {
                "bar": "📊", "line": "📈", "pie": "🥧", "area": "📉",
                "doughnut": "🍩", "radar": "🎯", "bubble": "🫧", "scatter": "📍"
            }.get(chart_type, "📊")

            self.canvas.create_text(
                x + width / 2, y + height / 2,
                text=f"{icon}\n{chart_type.title()} Chart\n(Preview)",
                font=("Microsoft YaHei", max(10, int(14 * self.scale))),
                fill=COLOR_TEXT_LIGHT,
                anchor="center",
                tags="element",
            )

    def draw_table(self, elem: Dict[str, Any], default_unit: str):
        """Draw table, supports more styles"""
        slide_w, slide_h = self.slide_size
        x, y, width, height = self._resolve_box_px(elem.get("box", {}), slide_w, slide_h, default_unit)

        x *= self.scale
        y *= self.scale
        width *= self.scale
        height *= self.scale

        table_cfg = elem.get("table", {})
        header = table_cfg.get("header") or []
        rows = table_cfg.get("rows") or []

        rows_count = len(rows) + (1 if header else 0)
        cols_count = len(header) if header else (len(rows[0]) if rows else 0)

        if rows_count == 0 or cols_count == 0:
            return

        cell_width = width / cols_count
        cell_height = height / rows_count

        all_rows: List[List[Any]] = []
        if header:
            all_rows.append(header)
        all_rows.extend(rows)

        # Table style
        style_cfg = table_cfg.get("style", {})
        banded_rows = table_cfg.get("bandedRows", False)
        banded_cols = table_cfg.get("bandedColumns", False)

        for i, row in enumerate(all_rows):
            for j in range(cols_count):
                cell_x0 = x + j * cell_width
                cell_y0 = y + i * cell_height
                cell_x1 = cell_x0 + cell_width
                cell_y1 = cell_y0 + cell_height

                # Cell background color
                if i == 0 and header:
                    # Header
                    bg_color = "#f3f4f6"
                    if style_cfg.get("header", {}).get("fill"):
                        bg_color = self.resolve_color(style_cfg["header"]["fill"])
                    font = ("Microsoft YaHei", max(10, int(12 * self.scale)), "bold")
                    text_color = self.resolve_color(style_cfg.get("header", {}).get("color", COLOR_TEXT))
                else:
                    # Body
                    bg_color = "white"
                    if banded_rows and (i - (1 if header else 0)) % 2 == 1:
                        bg_color = "#f9fafb"
                    if banded_cols and j % 2 == 1:
                        bg_color = "#f9fafb"
                    if style_cfg.get("body", {}).get("fill"):
                        bg_color = self.resolve_color(style_cfg["body"]["fill"])
                    font = ("Microsoft YaHei", max(9, int(11 * self.scale)))
                    text_color = self.resolve_color(style_cfg.get("body", {}).get("color", COLOR_TEXT_LIGHT))

                self.canvas.create_rectangle(
                    cell_x0, cell_y0, cell_x1, cell_y1,
                    fill=bg_color, outline=COLOR_BORDER, width=1, tags="element"
                )

                text = str(row[j]) if j < len(row) else ""
                self.canvas.create_text(
                    (cell_x0 + cell_x1) / 2,
                    (cell_y0 + cell_y1) / 2,
                    text=text,
                    font=font,
                    fill=text_color,
                    anchor="center",
                    width=cell_width - 10,
                    tags="element",
                )

    def draw_element(self, elem: Dict[str, Any], default_unit: str):
        """Unified entry point for drawing elements"""
        elem_type = elem.get("type")
        try:
            if elem_type == "text":
                self.draw_text(elem, default_unit)
            elif elem_type == "image":
                self.draw_image(elem, default_unit)
            elif elem_type == "shape":
                self.draw_shape(elem, default_unit)
            elif elem_type == "chart":
                self.draw_chart(elem, default_unit)
            elif elem_type == "table":
                self.draw_table(elem, default_unit)
            elif elem_type == "line":
                self.draw_line(elem, default_unit)
            elif elem_type == "icon":
                self.draw_icon(elem, default_unit)
            elif elem_type == "group":
                self.draw_group(elem, default_unit)
            elif elem_type == "video":
                self.draw_video(elem, default_unit)
            elif elem_type == "smartArt":
                self.draw_smartart(elem, default_unit)
        except Exception as e:
            logger.error(f"Element rendering failed: type={elem_type}, error={e}")

    def render_slide(self, slide_cfg: Dict[str, Any]):
        """Render single slide"""
        self.canvas.delete("all")
        self.slide_images.clear()

        if not slide_cfg:
            self.canvas.create_text(
                PREVIEW_MAX_WIDTH / 2,
                PREVIEW_MAX_HEIGHT / 2,
                text="No slides",
                font=("Microsoft YaHei", 16),
                fill=COLOR_TEXT_LIGHT,
            )
            return

        slide_w, slide_h = self.slide_size
        scaled_w = slide_w * self.scale
        scaled_h = slide_h * self.scale

        self.canvas.config(width=scaled_w, height=scaled_h)

        # Render background
        self.render_background(slide_cfg)

        default_unit = self.current_meta.get("ppt", {}).get("defaultUnit", "px") if self.current_meta else "px"

        # Get all elements and sort by zIndex
        elements = slide_cfg.get("elements", [])
        sorted_elements = sorted(elements, key=lambda e: e.get("zIndex", 0))

        # Render all elements
        for elem in sorted_elements:
            self.draw_element(elem, default_unit)

        # Show transition information (if any)
        transition = slide_cfg.get("transition")
        if transition and transition.get("type") != "none":
            transition_type = transition.get("type", "fade")
            duration = transition.get("duration", 1)
            # Show transition mark in corner
            self.canvas.create_text(
                scaled_w - 10, scaled_h - 10,
                text=f"🎬 {transition_type} ({duration}s)",
                font=("Microsoft YaHei", 9),
                fill=COLOR_TEXT_LIGHT,
                anchor="se",
                tags="transition_info"
            )

    def render(self):
        """Render current slide"""
        if not self.slides:
            self.canvas.delete("all")
            self.canvas.config(width=PREVIEW_MAX_WIDTH, height=PREVIEW_MAX_HEIGHT / 2)
            self.canvas.create_text(
                PREVIEW_MAX_WIDTH / 2,
                PREVIEW_MAX_HEIGHT / 4,
                text="📝 Add slides to see preview",
                font=("Microsoft YaHei", 18),
                fill=COLOR_TEXT_LIGHT,
            )
            return

        slide_cfg = self.slides[self.current_slide_index]
        self.render_slide(slide_cfg)

    def next_slide(self):
        """Switch to next slide"""
        if self.current_slide_index < len(self.slides) - 1:
            self.current_slide_index += 1
            logger.info("Switch to next page: index=%s", self.current_slide_index)
            self.render()

    def prev_slide(self):
        """Switch to previous slide"""
        if self.current_slide_index > 0:
            self.current_slide_index -= 1
            logger.info("Switch to previous page: index=%s", self.current_slide_index)
            self.render()


class JSONPPTApp:
    """Enhanced JSON to PPT Designer application"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("✨ JSON → PPT Designer (Enhanced)")
        self.root.geometry("1600x900")
        self.root.minsize(1200, 700)

        # Set application icon (if possible)
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass

        self.setup_styles()

        self.preview = None
        self.editor: Optional[ScrolledText] = None
        self.status_var = tk.StringVar()
        self.slide_info = tk.StringVar()
        self.render_job = None
        self.current_meta: Optional[Dict[str, Any]] = None
        self.error_line = None  # Record error line number

        self.setup_layout()
        self.setup_keyboard_shortcuts()
        self.load_sample()

    def setup_styles(self):
        """Set UI style"""
        style = ttk.Style()
        style.theme_use('clam')

        # Base style
        style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT)
        style.configure("Title.TLabel", font=("Microsoft YaHei", 12, "bold"))
        style.configure("Preview.TFrame", background=COLOR_BG)
        style.configure("Toolbar.TFrame", background=COLOR_SIDEBAR, relief="flat")
        style.configure("Status.TFrame", background=COLOR_SIDEBAR)
        style.configure("Status.TLabel", background=COLOR_SIDEBAR, foreground="white")

        # Button style
        style.configure("Toolbar.TButton",
                        background="#34495e",
                        foreground="white",
                        borderwidth=0,
                        focuscolor='none')
        style.map("Toolbar.TButton",
                  background=[('active', '#4a5f7a')])

    def setup_layout(self):
        """Set UI layout"""
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        self.create_toolbar(main_container)

        # Create main split panel
        paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left editor
        editor_frame = ttk.Frame(paned)
        paned.add(editor_frame, weight=1)

        editor_header = ttk.Frame(editor_frame)
        editor_header.pack(fill=tk.X, padx=10, pady=(10, 5))
        ttk.Label(editor_header, text="📝 JSON Editor", style="Title.TLabel").pack(side=tk.LEFT)

        # Editor toolbar
        editor_tools = ttk.Frame(editor_header)
        editor_tools.pack(side=tk.RIGHT)
        ttk.Button(editor_tools, text="🔍 Find", command=self.find_in_editor, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(editor_tools, text="↩️ Undo", command=self.undo_edit, width=8).pack(side=tk.LEFT, padx=2)

        editor_container = ttk.Frame(editor_frame)
        editor_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Line numbers
        line_number_frame = ttk.Frame(editor_container)
        line_number_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.line_numbers = tk.Text(
            line_number_frame,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            state='disabled',
            wrap='none',
            background='#34495e',
            foreground='#95a5a6'
        )
        self.line_numbers.pack(fill=tk.Y)

        # JSON editor
        self.editor = ScrolledText(
            editor_container,
            wrap=tk.NONE,
            font=("Consolas", 11),
            bg="#2d2d30",
            fg="#d4d4d4",
            insertbackground="#ffffff",
            selectbackground="#264f78",
            selectforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            undo=True,
            maxundo=-1
        )
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.bind("<<Modified>>", self.on_editor_modified)
        self.editor.bind("<KeyRelease>", self.update_line_numbers)
        self.editor.bind("<MouseWheel>", self.sync_scroll)

        # Right preview
        preview_frame = ttk.Frame(paned)
        paned.add(preview_frame, weight=1)

        preview_header = ttk.Frame(preview_frame)
        preview_header.pack(fill=tk.X, padx=10, pady=(10, 5))
        ttk.Label(preview_header, text="👁️ Live Preview", style="Title.TLabel").pack(side=tk.LEFT)

        # Navigation control
        nav_frame = ttk.Frame(preview_header)
        nav_frame.pack(side=tk.RIGHT)

        ttk.Button(nav_frame, text="⏮️", command=self.first_slide, width=3).pack(side=tk.LEFT, padx=1)
        ttk.Button(nav_frame, text="◀", command=self.prev_slide, width=3).pack(side=tk.LEFT, padx=1)
        self.slide_label = ttk.Label(nav_frame, textvariable=self.slide_info, font=("Microsoft YaHei", 10, "bold"))
        self.slide_label.pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="▶", command=self.next_slide, width=3).pack(side=tk.LEFT, padx=1)
        ttk.Button(nav_frame, text="⏭️", command=self.last_slide, width=3).pack(side=tk.LEFT, padx=1)

        # Zoom control
        ttk.Separator(nav_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Label(nav_frame, text="🔍").pack(side=tk.LEFT)
        self.zoom_var = tk.StringVar(value="Fit")
        zoom_combo = ttk.Combobox(nav_frame, textvariable=self.zoom_var, width=8, state="readonly")
        zoom_combo['values'] = ["50%", "75%", "100%", "125%", "150%", "Fit"]
        zoom_combo.pack(side=tk.LEFT, padx=2)
        zoom_combo.bind("<<ComboboxSelected>>", self.on_zoom_changed)

        self.preview = PPTPreview(preview_frame)
        self.preview.pack(fill=tk.BOTH, expand=True)

        self.create_statusbar()

    def create_toolbar(self, parent):
        """Create toolbar"""
        toolbar = ttk.Frame(parent, style="Toolbar.TFrame", height=50)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        btn_frame = ttk.Frame(toolbar, style="Toolbar.TFrame")
        btn_frame.pack(side=tk.LEFT, padx=10, pady=8)

        # File operations
        ttk.Button(btn_frame, text="📂 Open", command=self.open_file, style="Toolbar.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="💾 Save", command=self.save_file, style="Toolbar.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="📄 New", command=self.new_file, style="Toolbar.TButton").pack(side=tk.LEFT, padx=3)

        ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Edit operations
        ttk.Button(btn_frame, text="🎯 Format", command=self.format_json, style="Toolbar.TButton").pack(side=tk.LEFT,
                                                                                                       padx=3)
        ttk.Button(btn_frame, text="✅ Validate", command=self.validate_json, style="Toolbar.TButton").pack(side=tk.LEFT,
                                                                                                       padx=3)
        ttk.Button(btn_frame, text="🎨 Theme", command=self.show_theme_editor, style="Toolbar.TButton").pack(side=tk.LEFT,
                                                                                                           padx=3)

        ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Export operations
        ttk.Button(btn_frame, text="📤 Export PPT", command=self.export_ppt, style="Toolbar.TButton").pack(side=tk.LEFT,
                                                                                                       padx=3)
        ttk.Button(btn_frame, text="🖼️ Export Images", command=self.export_images, style="Toolbar.TButton").pack(
            side=tk.LEFT, padx=3)

        # Right quick actions
        quick_frame = ttk.Frame(toolbar, style="Toolbar.TFrame")
        quick_frame.pack(side=tk.RIGHT, padx=10, pady=8)

        ttk.Button(quick_frame, text="📚 Templates", command=self.show_templates, style="Toolbar.TButton").pack(side=tk.LEFT,
                                                                                                          padx=3)
        ttk.Button(quick_frame, text="❓ Help", command=self.show_help, style="Toolbar.TButton").pack(side=tk.LEFT,
                                                                                                     padx=3)

    def create_statusbar(self):
        """Create status bar"""
        statusbar = ttk.Frame(self.root, style="Status.TFrame", height=30)
        statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        statusbar.pack_propagate(False)

        self.status_label = ttk.Label(statusbar, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT, padx=15, pady=5)

        # Encoding information
        encoding_label = ttk.Label(statusbar, text="UTF-8", style="Status.TLabel")
        encoding_label.pack(side=tk.RIGHT, padx=5, pady=5)

        ttk.Separator(statusbar, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        # Position information
        self.position_var = tk.StringVar(value="Line 1, Column 1")
        position_label = ttk.Label(statusbar, textvariable=self.position_var, style="Status.TLabel")
        position_label.pack(side=tk.RIGHT, padx=10, pady=5)

        version_label = ttk.Label(statusbar, text="v2.0.0", style="Status.TLabel")
        version_label.pack(side=tk.RIGHT, padx=15, pady=5)

    def setup_keyboard_shortcuts(self):
        """Set keyboard shortcuts"""
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-e>", lambda e: self.export_ppt())
        self.root.bind("<Control-f>", lambda e: self.find_in_editor())
        self.root.bind("<F5>", lambda e: self.refresh_preview())
        self.root.bind("<Control-Left>", lambda e: self.prev_slide())
        self.root.bind("<Control-Right>", lambda e: self.next_slide())

        # Editor position update
        self.editor.bind("<KeyRelease>", self.update_cursor_position)
        self.editor.bind("<ButtonRelease-1>", self.update_cursor_position)

    def update_cursor_position(self, event=None):
        """Update cursor position display"""
        try:
            position = self.editor.index(tk.INSERT)
            line, col = position.split('.')
            self.position_var.set(f"Line {line}, Column {int(col) + 1}")
        except:
            pass

    def update_line_numbers(self, event=None):
        """Update line number display"""
        try:
            # Get total lines
            lines = self.editor.get("1.0", "end-1c").split("\n")
            line_numbers_text = "\n".join(str(i) for i in range(1, len(lines) + 1))

            # Update line numbers
            self.line_numbers.config(state='normal')
            self.line_numbers.delete('1.0', 'end')
            self.line_numbers.insert('1.0', line_numbers_text)
            self.line_numbers.config(state='disabled')

            # Sync scrolling
            self.sync_scroll()
        except:
            pass

    def sync_scroll(self, event=None):
        """Sync editor and line number scrolling"""
        try:
            self.line_numbers.yview_moveto(self.editor.yview()[0])
        except:
            pass

    def load_sample(self):
        """Load sample JSON"""
        sample_path = os.path.join(os.path.dirname(__file__), "sample.json")
        if os.path.exists(sample_path):
            try:
                with open(sample_path, "r", encoding="utf-8") as fp:
                    sample_text = fp.read()
            except:
                sample_text = SAMPLE_JSON
        else:
            sample_text = SAMPLE_JSON

        self.editor.insert("1.0", sample_text)
        self.editor.edit_modified(False)
        self.update_line_numbers()
        self.schedule_render()

    def on_editor_modified(self, event=None):
        """Editor content modification event"""
        if self.editor.edit_modified():
            self.editor.edit_modified(False)
            self.schedule_render()

    def schedule_render(self):
        """Schedule rendering (debounce)"""
        if self.render_job:
            self.root.after_cancel(self.render_job)
        self.render_job = self.root.after(DEBOUNCE_MS, self.refresh_preview)

    def refresh_preview(self):
        """Refresh preview"""
        if not self.editor:
            return

        content = self.editor.get("1.0", tk.END).strip()
        if not content:
            return

        try:
            meta = json.loads(content)
            validate(meta)
            self.current_meta = meta
            self.preview.set_meta(meta)
            self.update_slide_info()
            self.set_status("✅ JSON Valid", COLOR_SUCCESS)
            self.clear_error_highlight()
        except json.JSONDecodeError as exc:
            self.show_error(f"JSON Syntax Error: line {exc.lineno} - {exc.msg}")
            self.highlight_error_line(exc.lineno)
        except ValueError as exc:
            self.show_error(f"Validation Failed: {exc}")
        except Exception as exc:
            self.show_error(f"Error: {exc}")

    def highlight_error_line(self, line_no: int):
        """Highlight error line"""
        try:
            self.clear_error_highlight()
            self.error_line = line_no
            start = f"{line_no}.0"
            end = f"{line_no}.end"
            self.editor.tag_add("error", start, end)
            self.editor.tag_config("error", background="#ffcccc")
            self.editor.see(start)
        except:
            pass

    def clear_error_highlight(self):
        """Clear error highlight"""
        try:
            self.editor.tag_remove("error", "1.0", tk.END)
        except:
            pass

    def show_error(self, message: str):
        """Show error information"""
        self.preview.canvas.delete("all")
        self.preview.canvas.config(width=PREVIEW_MAX_WIDTH, height=PREVIEW_MAX_HEIGHT / 2)

        # Error icon and message
        error_text = f"❌ {message}"
        self.preview.canvas.create_text(
            PREVIEW_MAX_WIDTH / 2,
            PREVIEW_MAX_HEIGHT / 4 - 20,
            text=error_text,
            font=("Microsoft YaHei", 14),
            fill=COLOR_ERROR,
            width=PREVIEW_MAX_WIDTH - 40,
            tags="error"
        )

        # Tip information
        self.preview.canvas.create_text(
            PREVIEW_MAX_WIDTH / 2,
            PREVIEW_MAX_HEIGHT / 4 + 30,
            text="💡 Tip: Check JSON format, ensure all quotes, commas and brackets are correct",
            font=("Microsoft YaHei", 11),
            fill=COLOR_TEXT_LIGHT,
            width=PREVIEW_MAX_WIDTH - 60,
            tags="hint"
        )

        self.set_status(message, COLOR_ERROR)
        self.current_meta = None
        self.preview.slides = []
        self.slide_info.set("")

    def set_status(self, message: str, color: str = COLOR_INFO):
        """Set status bar message"""
        self.status_var.set(message)
        # Can add color change effect

    def new_file(self):
        """New file"""
        if self.editor.edit_modified():
            result = messagebox.askyesnocancel("New File", "Current file has been modified. Save?")
            if result is None:
                return
            elif result:
                self.save_file()

        self.editor.delete("1.0", tk.END)
        # Insert base template
        template = {
            "version": "1.0",
            "ppt": {
                "size": {"width": 1280, "height": 720, "unit": "px"},
                "defaultUnit": "px",
                "slides": []
            }
        }
        self.editor.insert("1.0", json.dumps(template, ensure_ascii=False, indent=2))
        self.editor.edit_modified(False)
        self.update_line_numbers()
        self.schedule_render()

    def format_json(self):
        """Format JSON"""
        try:
            content = self.editor.get("1.0", tk.END)
            parsed = json.loads(content)
            formatted = json.dumps(parsed, ensure_ascii=False, indent=2)

            # Save current cursor position
            cursor_pos = self.editor.index(tk.INSERT)

            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", formatted)

            # Try to restore cursor position
            try:
                self.editor.mark_set(tk.INSERT, cursor_pos)
            except:
                pass

            self.update_line_numbers()
            self.set_status("✨ JSON Formatted", COLOR_SUCCESS)
        except Exception as exc:
            self.set_status(f"Format Failed: {exc}", COLOR_ERROR)

    def validate_json(self):
        """Validate JSON"""
        try:
            content = self.editor.get("1.0", tk.END)
            meta = json.loads(content)
            validate(meta)

            # Statistics information
            slides_count = len(meta.get("ppt", {}).get("slides", []))
            elements_count = sum(len(s.get("elements", [])) for s in meta.get("ppt", {}).get("slides", []))

            message = f"JSON Validation Passed!\n\n" \
                      f"📊 Statistics:  \n" \
                      f"• Number of slides: {slides_count}\n" \
                      f"• Total elements: {elements_count}\n" \
                      f"• File size: {len(content)} characters"

            self.set_status("✅ JSON Validation Passed", COLOR_SUCCESS)
            messagebox.showinfo("Validation Passed", message)
        except Exception as exc:
            self.set_status(f"Validation Failed: {exc}", COLOR_ERROR)
            messagebox.showerror("Validation Failed", str(exc))

    def open_file(self):
        """Open file"""
        file_path = filedialog.askopenfilename(
            title="选择JSON文件",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as fp:
                data = fp.read()

            # Validate JSON format first
            json.loads(data)

            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", data)
            self.editor.edit_modified(False)
            self.update_line_numbers()
            self.set_status(f"✅ Loaded: {os.path.basename(file_path)}", COLOR_SUCCESS)

            # Save current file path
            self.current_file_path = file_path
            self.root.title(f"✨ JSON → PPT Designer - {os.path.basename(file_path)}")

        except json.JSONDecodeError as e:
            messagebox.showerror("Open File Failed", f"JSON format error: {e}")
        except Exception as exc:
            messagebox.showerror("Open File Failed", str(exc))

    def save_file(self):
        """Save file"""
        # If have current file path, save directly
        if hasattr(self, 'current_file_path') and self.current_file_path:
            file_path = self.current_file_path
        else:
            file_path = filedialog.asksaveasfilename(
                title="保存JSON文件",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )

        if not file_path:
            return

        try:
            content = self.editor.get("1.0", tk.END)
            # Validate JSON format
            json.loads(content)

            with open(file_path, "w", encoding="utf-8") as fp:
                fp.write(content.strip())

            self.editor.edit_modified(False)
            self.set_status(f"✅ Saved: {os.path.basename(file_path)}", COLOR_SUCCESS)
            self.current_file_path = file_path
            self.root.title(f"✨ JSON → PPT Designer - {os.path.basename(file_path)}")

        except json.JSONDecodeError:
            messagebox.showerror("Save Failed", "JSON format error, please fix errors first")
        except Exception as exc:
            messagebox.showerror("Save Failed", str(exc))

    def export_ppt(self):
        """Export PPT file"""
        if not self.current_meta:
            messagebox.showerror("Export PPT", "Please fix JSON errors first.")
            return

        file_path = filedialog.asksaveasfilename(
            title="导出PPT文件",
            defaultextension=".pptx",
            filetypes=[("PowerPoint files", "*.pptx")]
        )
        if not file_path:
            return

        try:
            self.set_status("⏳ Exporting PPT...", COLOR_INFO)
            self.root.update()

            prs, slide_count = build(self.current_meta, logger)
            prs.save(file_path)

            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)

            self.set_status(f"✅ Export Success: {os.path.basename(file_path)} ({file_size_mb:.2f} MB)", COLOR_SUCCESS)

            result = messagebox.askyesno(
                "导出Success",
                f"PPT exported successfully!\n\n"
                f"📊 File Information:\n"
                f"• Number of slides: {slide_count}\n"
                f"• File size: {file_size_mb:.2f} MB\n"
                f"• Save location: {file_path}\n\n"
                f"Open file immediately?"
            )

            if result:
                self.open_file_in_system(file_path)

        except Exception as exc:
            logger.exception("Export Failed")
            messagebox.showerror("Export Failed", f"Error during export process:\n{str(exc)}")
            self.set_status("❌ Export Failed", COLOR_ERROR)

    def export_images(self):
        """Export as image"""
        if not self.current_meta:
            messagebox.showerror("Export Images", "Please fix JSON errors first.")
            return

        folder_path = filedialog.askdirectory(title="选择导出文件夹")
        if not folder_path:
            return

        try:
            self.set_status("⏳ Exporting images...", COLOR_INFO)
            slides = self.current_meta.get("ppt", {}).get("slides", [])

            for i, slide in enumerate(slides):
                # Temporarily switch to slide and render
                self.preview.current_slide_index = i
                self.preview.render_slide(slide)

                # Get canvas content and save as image
                ps = self.preview.canvas.postscript(colormode='color')
                img = Image.open(io.BytesIO(ps.encode('utf-8').encode('latin-1')))

                # Save image
                img_path = os.path.join(folder_path, f"slide_{i + 1:03d}.png")
                img.save(img_path, "PNG")

            self.set_status(f"✅ Exported {len(slides)} images to: {folder_path}", COLOR_SUCCESS)
            messagebox.showinfo("Export Success", f"Successfully exported {len(slides)} images!")

            # Restore original slide
            self.preview.render()

        except Exception as e:
            logger.exception("Export Images Failed")
            messagebox.showerror("Export Failed", f"Error while exporting images:\n{str(e)}")

    def open_file_in_system(self, file_path: str):
        """Open file in system"""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                import subprocess
                subprocess.call(["open", file_path])
            else:  # Linux
                import subprocess
                subprocess.call(["xdg-open", file_path])
        except Exception as e:
            logger.error(f"Cannot open file: {e}")

    def show_theme_editor(self):
        """Show theme editor"""
        theme_window = tk.Toplevel(self.root)
        theme_window.title("🎨 Theme Editor")
        theme_window.geometry("600x400")

        # Simple theme editor interface
        ttk.Label(theme_window, text="主题编辑器", font=("Microsoft YaHei", 16, "bold")).pack(pady=10)

        # Color settings
        colors_frame = ttk.LabelFrame(theme_window, text="颜色设置", padding=10)
        colors_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Get current theme
        current_theme = self.current_meta.get("ppt", {}).get("theme", {}) if self.current_meta else {}
        current_colors = current_theme.get("colors", {})

        color_vars = {}
        for i, (key, default_color) in enumerate([
            ("primary", "#3B82F6"),
            ("secondary", "#10B981"),
            ("accent", "#F59E0B"),
            ("danger", "#EF4444")
        ]):
            row_frame = ttk.Frame(colors_frame)
            row_frame.grid(row=i, column=0, sticky="ew", pady=5)

            ttk.Label(row_frame, text=f"{key}:").pack(side=tk.LEFT, padx=5)

            color_var = tk.StringVar(value=current_colors.get(key, default_color))
            color_vars[key] = color_var

            color_entry = ttk.Entry(row_frame, textvariable=color_var, width=10)
            color_entry.pack(side=tk.LEFT, padx=5)

            color_button = tk.Button(row_frame, text="选择", width=6,
                                     command=lambda k=key, v=color_var: self.choose_color(k, v))
            color_button.pack(side=tk.LEFT, padx=5)

            # Color preview
            preview_label = tk.Label(row_frame, width=10, bg=color_var.get())
            preview_label.pack(side=tk.LEFT, padx=5)
            color_var.trace("w", lambda *args, l=preview_label, v=color_var: l.config(bg=v.get()))

        # Font settings
        fonts_frame = ttk.LabelFrame(theme_window, text="字体设置", padding=10)
        fonts_frame.pack(fill=tk.X, padx=20, pady=10)

        current_fonts = current_theme.get("fonts", {})

        ttk.Label(fonts_frame, text="标题字体:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        heading_font_var = tk.StringVar(value=current_fonts.get("heading", "Microsoft YaHei"))
        ttk.Entry(fonts_frame, textvariable=heading_font_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(fonts_frame, text="正文字体:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        body_font_var = tk.StringVar(value=current_fonts.get("body", "Arial"))
        ttk.Entry(fonts_frame, textvariable=body_font_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        # Apply button
        def apply_theme():
            try:
                # Update theme to current JSON
                if self.current_meta:
                    if "theme" not in self.current_meta.get("ppt", {}):
                        self.current_meta["ppt"]["theme"] = {}

                    self.current_meta["ppt"]["theme"]["colors"] = {
                        k: v.get() for k, v in color_vars.items()
                    }
                    self.current_meta["ppt"]["theme"]["fonts"] = {
                        "heading": heading_font_var.get(),
                        "body": body_font_var.get()
                    }

                    # Update editor
                    self.editor.delete("1.0", tk.END)
                    self.editor.insert("1.0", json.dumps(self.current_meta, ensure_ascii=False, indent=2))

                    self.set_status("✅ Theme Applied", COLOR_SUCCESS)
                    theme_window.destroy()
            except Exception as e:
                messagebox.showerror("Application Failed", str(e))

        ttk.Button(theme_window, text="应用主题", command=apply_theme).pack(pady=20)

    def choose_color(self, key: str, var: tk.StringVar):
        """Select color"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(initialcolor=var.get())
        if color[1]:
            var.set(color[1])

    def show_templates(self):
        """Show template library"""
        template_window = tk.Toplevel(self.root)
        template_window.title("📚 Template Library")
        template_window.geometry("800x600")

        # Template list
        templates = [
            {
                "name": "Business Presentation",
                "description": "Professional business presentation template with cover, TOC, content and ending",
                "preview": "🏢",
                "data": self._get_business_template()
            },
            {
                "name": "Educational Courseware",
                "description": "Courseware template for teaching with title, concepts and exercises",
                "preview": "📚",
                "data": self._get_education_template()
            },
            {
                "name": "Product Introduction",
                "description": "Product showcase template with features, comparison and pricing",
                "preview": "📱",
                "data": self._get_product_template()
            },
            {
                "name": "Data Report",
                "description": "Data analysis report template with various charts",
                "preview": "📊",
                "data": self._get_data_template()
            }
        ]

        # Create template grid
        for i, template in enumerate(templates):
            frame = ttk.Frame(template_window, relief=tk.RAISED, borderwidth=1)
            frame.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")

            # Template preview
            preview_label = tk.Label(frame, text=template["preview"], font=("Arial", 48))
            preview_label.pack(pady=10)

            # Template name
            name_label = ttk.Label(frame, text=template["name"], font=("Microsoft YaHei", 14, "bold"))
            name_label.pack()

            # Template description
            desc_label = ttk.Label(frame, text=template["description"], wraplength=300)
            desc_label.pack(pady=5)

            # Use button
            use_button = ttk.Button(frame, text="使用此模板",
                                    command=lambda t=template: self.use_template(t, template_window))
            use_button.pack(pady=10)

        # Configure grid weights
        template_window.grid_rowconfigure(0, weight=1)
        template_window.grid_rowconfigure(1, weight=1)
        template_window.grid_columnconfigure(0, weight=1)
        template_window.grid_columnconfigure(1, weight=1)

    def use_template(self, template: dict, window: tk.Toplevel):
        """Use template"""
        if self.editor.edit_modified():
            result = messagebox.askyesno("Use Template", "Current file has been modified. Use template will overwrite current content. Continue?")
            if not result:
                return

        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", json.dumps(template["data"], ensure_ascii=False, indent=2))
        self.editor.edit_modified(False)
        self.update_line_numbers()
        self.schedule_render()

        window.destroy()
        self.set_status(f"✅ Template Loaded: {template['name']}", COLOR_SUCCESS)

    def _get_business_template(self) -> dict:
        """Get business template"""
        return {
            "version": "1.0",
            "ppt": {
                "size": {"width": 1280, "height": 720, "unit": "px"},
                "defaultUnit": "px",
                "theme": {
                    "colors": {
                        "primary": "#1e40af",
                        "secondary": "#64748b",
                        "accent": "#f59e0b"
                    },
                    "fonts": {
                        "heading": "Microsoft YaHei",
                        "body": "Arial"
                    }
                },
                "slides": [
                    {
                        "id": "cover",
                        "background": {
                            "gradient": {
                                "type": "linear",
                                "angle": 135,
                                "stops": [
                                    {"color": "#1e40af", "position": 0},
                                    {"color": "#3730a3", "position": 100}
                                ]
                            }
                        },
                        "elements": [
                            {
                                "type": "text",
                                "text": "Business Presentation Title",
                                "box": {"x": 640, "y": 300, "w": 800, "h": 100},
                                "style": {"fontSize": 56, "color": "#ffffff", "align": "center", "bold": True}
                            },
                            {
                                "type": "text",
                                "text": "Subtitle Text",
                                "box": {"x": 640, "y": 400, "w": 600, "h": 60},
                                "style": {"fontSize": 28, "color": "#e0e7ff", "align": "center"}
                            }
                        ]
                    }
                ]
            }
        }

    def _get_education_template(self) -> dict:
        """Get education template"""
        return {
            "version": "1.0",
            "ppt": {
                "size": {"width": 1280, "height": 720, "unit": "px"},
                "defaultUnit": "px",
                "theme": {
                    "colors": {
                        "primary": "#059669",
                        "secondary": "#34d399",
                        "accent": "#fbbf24"
                    }
                },
                "slides": [
                    {
                        "id": "title",
                        "background": {"color": "#ecfdf5"},
                        "elements": [
                            {
                                "type": "text",
                                "text": "Course Title",
                                "box": {"x": 640, "y": 300, "w": 800, "h": 100},
                                "style": {"fontSize": 48, "color": "$primary", "align": "center", "bold": True}
                            }
                        ]
                    }
                ]
            }
        }

    def _get_product_template(self) -> dict:
        """Get product template"""
        return {
            "version": "1.0",
            "ppt": {
                "size": {"width": 1280, "height": 720, "unit": "px"},
                "defaultUnit": "px",
                "slides": [
                    {
                        "id": "product",
                        "background": {"color": "#ffffff"},
                        "elements": [
                            {
                                "type": "text",
                                "text": "Product Name",
                                "box": {"x": 100, "y": 100, "w": 600, "h": 80},
                                "style": {"fontSize": 42, "color": "#1f2937", "bold": True}
                            }
                        ]
                    }
                ]
            }
        }

    def _get_data_template(self) -> dict:
        """Get data template"""
        return {
            "version": "1.0",
            "ppt": {
                "size": {"width": 1280, "height": 720, "unit": "px"},
                "defaultUnit": "px",
                "slides": [
                    {
                        "id": "data",
                        "background": {"color": "#f9fafb"},
                        "elements": [
                            {
                                "type": "text",
                                "text": "Data Analysis Report",
                                "box": {"x": 640, "y": 50, "w": 800, "h": 80},
                                "style": {"fontSize": 36, "color": "#111827", "align": "center", "bold": True}
                            },
                            {
                                "type": "chart",
                                "chartType": "bar",
                                "box": {"x": 100, "y": 150, "w": 500, "h": 400},
                                "data": {
                                    "categories": ["Q1", "Q2", "Q3", "Q4"],
                                    "series": [
                                        {"name": "Sales Revenue", "values": [100, 150, 120, 180]}
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }
        }

    def show_help(self):
        """Show help"""
        help_window = tk.Toplevel(self.root)
        help_window.title("❓ Help")
        help_window.geometry("700x500")

        # Create notebook
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Shortcuts page
        shortcuts_frame = ttk.Frame(notebook)
        notebook.add(shortcuts_frame, text="快捷键")

        shortcuts_text = ScrolledText(shortcuts_frame, wrap=tk.WORD, height=20)
        shortcuts_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        shortcuts_text.insert("1.0", """
Keyboard Shortcuts:

File Operations:
  Ctrl+N    New File
  Ctrl+O    Open File
  Ctrl+S    Save File
  Ctrl+E    Export PPT

Edit Operations:
  Ctrl+F    Find
  Ctrl+Z    Undo
  Ctrl+Y    Redo
  F5        Refresh Preview

Navigation:
  Ctrl+←    Previous Page
  Ctrl+→    Next Page
  Home      First Page
  End       Last Page

Other:
  Ctrl+H    Show Help
  Esc       Close Dialog
        """)
        shortcuts_text.config(state='disabled')

        # Element types page
        elements_frame = ttk.Frame(notebook)
        notebook.add(elements_frame, text="元素类型")

        elements_text = ScrolledText(elements_frame, wrap=tk.WORD, height=20)
        elements_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        elements_text.insert("1.0", """
Supported Element Types:

📝 text - Text Element
   Supports styles, paragraphs, lists, etc.

🖼️ image - Image Element
   Supports local files, URLs, base64

📊 chart - Chart Element
   Bar chart, line chart, pie chart, radar chart, etc.

🔷 shape - Shape Element
   Rectangle, circle, star, arrow, etc. 30+ types

📋 table - Table Element
   Supports styles, striped rows and columns

➖ line - Line Element
   Supports arrows, curves

⭐ icon - Icon Element
   Supports multiple icon libraries

👥 group - Group Element
   Combine multiple elements

🎬 video - Video Element
   Video placeholder

🎯 smartArt - SmartArt
   Flowchart, circular diagram, etc.
        """)
        elements_text.config(state='disabled')

        # About page
        about_frame = ttk.Frame(notebook)
        notebook.add(about_frame, text="关于")

        about_text = ScrolledText(about_frame, wrap=tk.WORD, height=20)
        about_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        about_text.insert("1.0", """
JSON → PPT Designer v2.0.0

A powerful JSON to PowerPoint conversion tool that supports:
• Real-time preview
• Rich element types
• Theme system
• Gradient and shadow effects
• Multiple chart types
• SmartArt

Author: AI Assistant
License: MIT License

Thank you for using!
        """)
        about_text.config(state='disabled')

    def find_in_editor(self):
        """Find in editor"""
        find_window = tk.Toplevel(self.root)
        find_window.title("Find")
        find_window.geometry("400x100")

        ttk.Label(find_window, text="查找内容:").grid(row=0, column=0, padx=5, pady=5)

        find_var = tk.StringVar()
        find_entry = ttk.Entry(find_window, textvariable=find_var, width=30)
        find_entry.grid(row=0, column=1, padx=5, pady=5)
        find_entry.focus()

        def do_find():
            search_text = find_var.get()
            if not search_text:
                return

            # Clear previous highlight
            self.editor.tag_remove("found", "1.0", tk.END)

            # Search text
            start = "1.0"
            while True:
                pos = self.editor.search(search_text, start, tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(search_text)}c"
                self.editor.tag_add("found", pos, end)
                start = end

            # Configure highlight style
            self.editor.tag_config("found", background="#ffff00")

            # Jump to first match
            first = self.editor.search(search_text, "1.0", tk.END)
            if first:
                self.editor.see(first)

        ttk.Button(find_window, text="查找", command=do_find).grid(row=0, column=2, padx=5, pady=5)

        # Bind enter key
        find_entry.bind("<Return>", lambda e: do_find())

    def undo_edit(self):
        """Undo edit"""
        try:
            self.editor.edit_undo()
        except:
            pass

    def next_slide(self):
        """Next page"""
        self.preview.next_slide()
        self.update_slide_info()

    def prev_slide(self):
        """Previous page"""
        self.preview.prev_slide()
        self.update_slide_info()

    def first_slide(self):
        """First page"""
        if self.preview.slides:
            self.preview.current_slide_index = 0
            self.preview.render()
            self.update_slide_info()

    def last_slide(self):
        """Last page"""
        if self.preview.slides:
            self.preview.current_slide_index = len(self.preview.slides) - 1
            self.preview.render()
            self.update_slide_info()

    def on_zoom_changed(self, event=None):
        """Zoom change"""
        zoom_value = self.zoom_var.get()
        if zoom_value == "Fit":
            # Restore adaptive scaling
            if self.preview.current_meta:
                self.preview.set_meta(self.preview.current_meta)
        else:
            # Set fixed scaling
            try:
                zoom_percent = int(zoom_value.rstrip('%'))
                self.preview.scale = zoom_percent / 100.0
                self.preview.render()
            except:
                pass

    def update_slide_info(self):
        """Update slide information"""
        total_slides = len(self.preview.slides)
        if total_slides:
            current = self.preview.current_slide_index + 1
            slide_id = self.preview.slides[self.preview.current_slide_index].get("id", "")
            if slide_id:
                self.slide_info.set(f"{current} / {total_slides} [{slide_id}]")
            else:
                self.slide_info.set(f"{current} / {total_slides}")
        else:
            self.slide_info.set("0 / 0")


def main():
    """Main function"""
    root = tk.Tk()

    # Set DPI awareness（Windows）
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    # Set application icon
    try:
        if platform.system() == "Windows":
            root.iconbitmap(default='icon.ico')
    except:
        pass

    app = JSONPPTApp(root)

    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()