"""
Design System & Theme Configuration for Contract Risk Review Frontend.
Provides consistent colors, spacing, typography, and CSS generation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal
import streamlit as st


# ═══════════════════════════════════════════════════════════════════════════════
# Color Palettes
# ═══════════════════════════════════════════════════════════════════════════════

# Light theme colors
LIGHT_COLORS = {
    # Primary brand
    "primary": "#1E3A8A",          # Blue-900
    "primary_light": "#3B82F6",    # Blue-500
    "primary_dark": "#1E40AF",     # Blue-800
    "primary_bg": "#EFF6FF",       # Blue-50
    
    # Neutral grays
    "bg_primary": "#F8FAFC",       # Slate-50
    "bg_secondary": "#FFFFFF",     # White
    "bg_tertiary": "#F1F5F9",      # Slate-100
    "bg_card": "#FFFFFF",          # White
    "bg_hover": "#F1F5F9",         # Slate-100
    
    # Text
    "text_primary": "#0F172A",     # Slate-900
    "text_secondary": "#475569",   # Slate-600
    "text_muted": "#94A3B8",       # Slate-400
    "text_inverse": "#FFFFFF",     # White
    
    # Borders
    "border_light": "#E2E8F0",     # Slate-200
    "border_medium": "#CBD5E1",    # Slate-300
    "border_dark": "#94A3B8",      # Slate-400
    
    # Severity colors (matching existing)
    "severity_critical": "#DC2626",  # Red-600
    "severity_critical_bg": "#FEF2F2",  # Red-50
    "severity_high": "#EA580C",      # Orange-600
    "severity_high_bg": "#FFF7ED",   # Orange-50
    "severity_medium": "#D97706",    # Amber-600
    "severity_medium_bg": "#FFFBEB", # Amber-50
    "severity_low": "#65A30D",       # Green-600
    "severity_low_bg": "#F7FEE7",    # Green-50
    "severity_none": "#16A34A",      # Green-600
    "severity_none_bg": "#F0FDF4",   # Green-50
    
    # Recommendation colors
    "rec_approve": "#16A34A",            # Green-600
    "rec_approve_bg": "#F0FDF4",         # Green-50
    "rec_approve_changes": "#D97706",    # Amber-600
    "rec_approve_changes_bg": "#FFFBEB", # Amber-50
    "rec_reject": "#DC2626",             # Red-600
    "rec_reject_bg": "#FEF2F2",          # Red-50
    
    # Status colors
    "success": "#16A34A",
    "success_bg": "#F0FDF4",
    "warning": "#D97706",
    "warning_bg": "#FFFBEB",
    "error": "#DC2626",
    "error_bg": "#FEF2F2",
    "info": "#2563EB",
    "info_bg": "#EFF6FF",
    
    # Shadows
    "shadow_sm": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
    "shadow_md": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
    "shadow_lg": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
}

# Dark theme colors
DARK_COLORS = {
    # Primary brand
    "primary": "#60A5FA",          # Blue-400
    "primary_light": "#93C5FD",    # Blue-300
    "primary_dark": "#3B82F6",     # Blue-500
    "primary_bg": "#1E3A5F",       # Dark blue
    
    # Neutral grays
    "bg_primary": "#0F172A",       # Slate-900
    "bg_secondary": "#1E293B",     # Slate-800
    "bg_tertiary": "#334155",      # Slate-700
    "bg_card": "#1E293B",          # Slate-800
    "bg_hover": "#334155",         # Slate-700
    
    # Text
    "text_primary": "#F8FAFC",     # Slate-50
    "text_secondary": "#CBD5E1",   # Slate-300
    "text_muted": "#64748B",       # Slate-500
    "text_inverse": "#0F172A",     # Slate-900
    
    # Borders
    "border_light": "#334155",     # Slate-700
    "border_medium": "#475569",    # Slate-600
    "border_dark": "#64748B",      # Slate-500
    
    # Severity colors (adjusted for dark mode)
    "severity_critical": "#F87171",   # Red-400
    "severity_critical_bg": "#7F1D1D",   # Red-900
    "severity_high": "#FB923C",       # Orange-400
    "severity_high_bg": "#7C2D12",    # Orange-900
    "severity_medium": "#FBBF24",     # Amber-400
    "severity_medium_bg": "#78350F",  # Amber-900
    "severity_low": "#86EFAC",        # Green-400
    "severity_low_bg": "#14532D",     # Green-900
    "severity_none": "#4ADE80",       # Green-400
    "severity_none_bg": "#14532D",    # Green-900
    
    # Recommendation colors
    "rec_approve": "#4ADE80",       # Green-400
    "rec_approve_bg": "#14532D",    # Green-900
    "rec_approve_changes": "#FBBF24", # Amber-400
    "rec_approve_changes_bg": "#78350F", # Amber-900
    "rec_reject": "#F87171",        # Red-400
    "rec_reject_bg": "#7F1D1D",     # Red-900
    
    # Status colors
    "success": "#4ADE80",
    "success_bg": "#14532D",
    "warning": "#FBBF24",
    "warning_bg": "#78350F",
    "error": "#F87171",
    "error_bg": "#7F1D1D",
    "info": "#60A5FA",
    "info_bg": "#1E3A5F",
    
    # Shadows
    "shadow_sm": "0 1px 2px 0 rgb(0 0 0 / 0.3)",
    "shadow_md": "0 4px 6px -1px rgb(0 0 0 / 0.4), 0 2px 4px -2px rgb(0 0 0 / 0.3)",
    "shadow_lg": "0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.3)",
}