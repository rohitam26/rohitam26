#!/usr/bin/env python3
import sys
import re

dragon_head = """<g class="s s0">
  <g transform="translate(-3, -4) scale(1.35)">
    <!-- Dragon Horns (Majestic Swept-back Horns) -->
    <path d="M 3 3 Q 0 -3 -2 -6 Q 1 -3 4 1 Z" fill="#38bdf8" stroke="#0284c7" stroke-width="0.4"/>
    <path d="M 10 3 Q 13 -3 15 -6 Q 12 -3 9 1 Z" fill="#38bdf8" stroke="#0284c7" stroke-width="0.4"/>
    
    <!-- Dragon Head Base -->
    <path d="M 2 5 Q 1 10 3 13 Q 6.5 15 10 13 Q 12 10 11 5 Q 6.5 2 2 5 Z" fill="#0284c7" stroke="#0369a1" stroke-width="0.5"/>
    
    <!-- Dragon Brow / Crest -->
    <polygon points="6.5,-1 5,3 8,3" fill="#38bdf8"/>
    <polygon points="6.5,2 4,5 9,5" fill="#0ea5e9"/>
    
    <!-- Dragon Wings -->
    <path d="M 1 6 Q -5 2 -7 5 Q -4 8 0 8 Z" fill="#0ea5e9" stroke="#0284c7" stroke-width="0.3"/>
    <path d="M 12 6 Q 18 2 20 5 Q 17 8 13 8 Z" fill="#0ea5e9" stroke="#0284c7" stroke-width="0.3"/>

    <!-- Glowing Amber / Golden Dragon Eyes -->
    <polygon points="3,6 5.5,5.5 5,8 3.2,7.8" fill="#fbbf24" stroke="#d97706" stroke-width="0.3"/>
    <line x1="4.2" y1="5.8" x2="4" y2="7.8" stroke="#0f172a" stroke-width="0.6" stroke-linecap="round"/>
    
    <polygon points="10,6 7.5,5.5 8,8 9.8,7.8" fill="#fbbf24" stroke="#d97706" stroke-width="0.3"/>
    <line x1="8.8" y1="5.8" x2="9" y2="7.8" stroke="#0f172a" stroke-width="0.6" stroke-linecap="round"/>

    <!-- Snout & Nostrils -->
    <ellipse cx="6.5" cy="11" rx="3.2" ry="2" fill="#0369a1"/>
    <circle cx="5.2" cy="11.2" r="0.5" fill="#38bdf8"/>
    <circle cx="7.8" cy="11.2" r="0.5" fill="#38bdf8"/>

    <!-- Dragon Fangs -->
    <polygon points="4.2,12.5 4.8,14.5 5.4,12.5" fill="#ffffff"/>
    <polygon points="7.6,12.5 8.2,14.5 8.8,12.5" fill="#ffffff"/>

    <!-- Whiskers / Draconic Tendrils -->
    <path d="M 3 11 Q 0 13 -1 16" fill="none" stroke="#38bdf8" stroke-width="0.5" stroke-linecap="round"/>
    <path d="M 10 11 Q 13 13 14 16" fill="none" stroke="#38bdf8" stroke-width="0.5" stroke-linecap="round"/>

    <!-- Flickering Cyan Fire Breath -->
    <path d="M 5.5 13 Q 6.5 17 7.5 13 Q 6.5 15.5 5.5 13 Z" fill="#38bdf8">
      <animate attributeName="opacity" values="0.5;1;0.3;0.9;0.5" dur="0.7s" repeatCount="indefinite"/>
    </path>
  </g>
</g>"""

dragon_s1 = """<g class="s s1">
  <g transform="translate(-1, -1) scale(1.15)">
    <rect x="0.5" y="0.5" width="11" height="11" rx="4" fill="#0284c7" stroke="#0369a1" stroke-width="0.5"/>
    <polygon points="6,-2 4,1 8,1" fill="#38bdf8"/>
    <circle cx="6" cy="6" r="2.5" fill="#0369a1" opacity="0.6"/>
  </g>
</g>"""

dragon_s2 = """<g class="s s2">
  <g transform="translate(-0.5, -0.5) scale(1.1)">
    <rect x="1" y="1" width="10" height="10" rx="3.5" fill="#0369a1" stroke="#075985" stroke-width="0.5"/>
    <polygon points="6,-1 4.5,1.5 7.5,1.5" fill="#38bdf8"/>
    <circle cx="6" cy="6" r="2" fill="#0284c7" opacity="0.6"/>
  </g>
</g>"""

dragon_s3 = """<g class="s s3">
  <g transform="translate(0, 0) scale(1.05)">
    <rect x="1.5" y="1.5" width="9" height="9" rx="3" fill="#075985"/>
    <polygon points="6,14 2,9 10,9" fill="#38bdf8" stroke="#0284c7" stroke-width="0.5"/>
    <circle cx="6" cy="14" r="1.5" fill="#67e8f9">
      <animate attributeName="r" values="1.2;2;1.2" dur="0.9s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.6;1;0.6" dur="0.9s" repeatCount="indefinite"/>
    </circle>
  </g>
</g>"""

def transform_to_dragon(svg_path):
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg = f.read()

    # Replace head .s.s0
    if re.search(r'<g class="s s0">.*?</g>', svg, flags=re.DOTALL):
        svg = re.sub(r'<g class="s s0">.*?</g>', dragon_head, svg, count=1, flags=re.DOTALL)
    elif '<g class="s s0"' in svg:
        svg = re.sub(r'<g class="s s0"[^>]*>.*?</g>', dragon_head, svg, count=1, flags=re.DOTALL)
    else:
        # Append before closing </svg>
        svg = svg.replace('</svg>', dragon_head + '\n</svg>')

    # Replace or add body segments
    if '<g class="s s1">' in svg:
        svg = re.sub(r'<g class="s s1">.*?</g>', dragon_s1, svg, count=1, flags=re.DOTALL)
    if '<g class="s s2">' in svg:
        svg = re.sub(r'<g class="s s2">.*?</g>', dragon_s2, svg, count=1, flags=re.DOTALL)
    if '<g class="s s3">' in svg:
        svg = re.sub(r'<g class="s s3">.*?</g>', dragon_s3, svg, count=1, flags=re.DOTALL)
    else:
        svg = re.sub(r'(</g>\s*</g>\s*)(</svg>)', r'\1' + dragon_s1 + '\n' + dragon_s2 + '\n' + dragon_s3 + r'\n\2', svg)

    # Set snake trail variable to electric cyan/blue
    svg = re.sub(r'--cs:[^;]+;', '--cs:#38bdf8;', svg)

    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Transformed {svg_path} into Azure Dragon!")

if __name__ == '__main__':
    for path in sys.argv[1:]:
        transform_to_dragon(path)
