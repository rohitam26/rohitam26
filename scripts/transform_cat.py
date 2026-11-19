#!/usr/bin/env python3
import sys
import re

def transform_to_cat(svg_path):
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg = f.read()

    cat_head = """<g class="s s0">
  <!-- Cat Head -->
  <rect x="0.8" y="2.2" width="14.4" height="12.2" rx="4" fill="#f59e0b"/>
  <!-- Left Ear -->
  <polygon points="1.5,4 4.5,0 7,4" fill="#f59e0b"/>
  <polygon points="2.5,3.8 4.5,1.2 6,3.8" fill="#fda4af"/>
  <!-- Right Ear -->
  <polygon points="9,4 11.5,0 14.5,4" fill="#f59e0b"/>
  <polygon points="10,3.8 11.5,1.2 13.5,3.8" fill="#fda4af"/>
  <!-- Eyes -->
  <circle cx="5" cy="7.5" r="1.3" fill="#1e293b"/>
  <circle cx="11" cy="7.5" r="1.3" fill="#1e293b"/>
  <circle cx="4.6" cy="7.1" r="0.4" fill="#ffffff"/>
  <circle cx="10.6" cy="7.1" r="0.4" fill="#ffffff"/>
  <!-- Pink Nose -->
  <polygon points="7.5,9.2 8.5,9.2 8,9.8" fill="#f43f5e"/>
  <!-- Whiskers -->
  <line x1="1" y1="8.5" x2="3.8" y2="8.8" stroke="#1e293b" stroke-width="0.6"/>
  <line x1="1" y1="10" x2="3.8" y2="9.8" stroke="#1e293b" stroke-width="0.6"/>
  <line x1="12.2" y1="8.8" x2="15" y2="8.5" stroke="#1e293b" stroke-width="0.6"/>
  <line x1="12.2" y1="9.8" x2="15" y2="10" stroke="#1e293b" stroke-width="0.6"/>
</g>"""

    cat_body = """<g class="s s1">
  <rect x="1.8" y="1.8" width="12.3" height="12.3" rx="4.1" fill="#f59e0b"/>
  <ellipse cx="8" cy="8" rx="3.5" ry="4" fill="#fef3c7"/>
</g>"""

    cat_hind = """<g class="s s2">
  <rect x="2.6" y="2.6" width="10.8" height="10.8" rx="3.6" fill="#d97706"/>
  <circle cx="4.5" cy="11.5" r="1.2" fill="#ffffff"/>
  <circle cx="11.5" cy="11.5" r="1.2" fill="#ffffff"/>
</g>"""

    cat_tail = """<g class="s s3">
  <rect x="3.0" y="3.0" width="9.9" height="9.9" rx="3.3" fill="#b45309"/>
  <path d="M 8 3 Q 11 0 13 2 Q 14 4 12 5" fill="none" stroke="#b45309" stroke-width="2.2" stroke-linecap="round"/>
  <circle cx="12" cy="5" r="1.2" fill="#fef3c7"/>
</g>"""

    # Replace snake rectangles with cat vector elements
    svg = re.sub(r'<rect class="s s0"[^>]*/>', cat_head, svg)
    svg = re.sub(r'<rect class="s s1"[^>]*/>', cat_body, svg)
    svg = re.sub(r'<rect class="s s2"[^>]*/>', cat_hind, svg)
    svg = re.sub(r'<rect class="s s3"[^>]*/>', cat_tail, svg)

    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Transformed {svg_path} into Animated Cat!")

if __name__ == '__main__':
    for path in sys.argv[1:]:
        transform_to_cat(path)
