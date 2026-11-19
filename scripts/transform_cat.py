#!/usr/bin/env python3
import sys
import re

def transform_to_cat(svg_path):
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg = f.read()

    cat_element = """<g class="s s0">
  <g transform="translate(-1.5, -2) scale(1.2)">
    <!-- Cat Head / Face -->
    <rect x="0.5" y="2.5" width="15" height="13" rx="4.5" fill="#f59e0b"/>
    <!-- Left Ear -->
    <polygon points="1.5,4.5 4,0 7,3.5" fill="#f59e0b"/>
    <polygon points="2.5,4 4,1 6,3.5" fill="#fda4af"/>
    <!-- Right Ear -->
    <polygon points="9,3.5 12,0 14.5,4.5" fill="#f59e0b"/>
    <polygon points="10,3.5 12,1 13.5,4" fill="#fda4af"/>
    <!-- Muzzle / Cheeks -->
    <ellipse cx="8" cy="11.5" rx="4.5" ry="3" fill="#fef3c7"/>
    <!-- Big Sparkling Eyes -->
    <ellipse cx="5" cy="8" rx="1.5" ry="1.8" fill="#1e293b"/>
    <ellipse cx="11" cy="8" rx="1.5" ry="1.8" fill="#1e293b"/>
    <circle cx="4.5" cy="7.3" r="0.6" fill="#ffffff"/>
    <circle cx="10.5" cy="7.3" r="0.6" fill="#ffffff"/>
    <circle cx="5.5" cy="8.8" r="0.3" fill="#ffffff"/>
    <circle cx="11.5" cy="8.8" r="0.3" fill="#ffffff"/>
    <!-- Pink Nose -->
    <polygon points="7.2,9.8 8.8,9.8 8,10.6" fill="#f43f5e"/>
    <!-- Cat Mouth (:3) -->
    <path d="M 6.8 11.2 Q 7.4 12.2 8 11.2 Q 8.6 12.2 9.2 11.2" fill="none" stroke="#1e293b" stroke-width="0.6" stroke-linecap="round"/>
    <!-- Whiskers -->
    <line x1="0" y1="9" x2="3" y2="9.5" stroke="#1e293b" stroke-width="0.6"/>
    <line x1="0" y1="11" x2="3" y2="10.5" stroke="#1e293b" stroke-width="0.6"/>
    <line x1="13" y1="9.5" x2="16" y2="9" stroke="#1e293b" stroke-width="0.6"/>
    <line x1="13" y1="10.5" x2="16" y2="11" stroke="#1e293b" stroke-width="0.6"/>
    <!-- Paws -->
    <ellipse cx="5" cy="15" rx="1.6" ry="1" fill="#ffffff" stroke="#f59e0b" stroke-width="0.5"/>
    <ellipse cx="11" cy="15" rx="1.6" ry="1" fill="#ffffff" stroke="#f59e0b" stroke-width="0.5"/>
  </g>
</g>"""

    # Replace s0 with the standalone cat
    svg = re.sub(r'<rect class="s s0"[^>]*/>', cat_element, svg)
    # Completely remove s1, s2, s3 (NO body segments, NO tail!)
    svg = re.sub(r'<rect class="s s1"[^>]*/>', '', svg)
    svg = re.sub(r'<rect class="s s2"[^>]*/>', '', svg)
    svg = re.sub(r'<rect class="s s3"[^>]*/>', '', svg)

    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Transformed {svg_path} into Cat (No Tail)!")

if __name__ == '__main__':
    for path in sys.argv[1:]:
        transform_to_cat(path)
