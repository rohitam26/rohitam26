#!/usr/bin/env python3
"""
Generate animated Tokyo-Night Activity Graph SVG with pure SMIL animations.
Fetches the last 31 days of contribution activity and renders:
- An animated path drawing with stroke-dashoffset loop
- Pulsing neon area gradient fill
- Pulsing cyan coordinate points
- A glowing neon tracking bead tracing the curve
"""

import urllib.request
import re
import os

def update_activity_graph():
    url = (
        "https://github-readme-activity-graph.vercel.app/graph"
        "?username=rohitam26&theme=tokyo-night&bg_color=0d1117"
        "&color=70a5fd&line=bf91f3&point=38bdae&area=true&hide_border=true"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    svg = urllib.request.urlopen(req).read().decode("utf-8")

    # Replace foreignObject header with pure SVG text
    header_svg = """
<g transform="translate(600, 36)">
  <text text-anchor="middle" fill="#70a5fd" font-family='"Segoe UI", Ubuntu, sans-serif' font-weight="700" font-size="20px">
    Rohita Muthu's Activity Graph
  </text>
</g>
"""
    svg = re.sub(r"<foreignObject.*?</foreignObject>", header_svg, svg, flags=re.DOTALL)

    # Extract line path d
    line_match = re.search(r'<path[^>]*class="ct-line"[^>]*d="([^"]+)"', svg)
    if not line_match:
        line_match = re.search(r'<path[^>]*d="([^"]+)"[^>]*class="ct-line"', svg)
    line_path_d = line_match.group(1) if line_match else ""

    # Add defs
    defs_block = """
<defs>
  <linearGradient id="animatedAreaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#bf91f3" stop-opacity="0.45">
      <animate attributeName="stop-opacity" values="0.2;0.55;0.2" dur="4s" repeatCount="indefinite" />
    </stop>
    <stop offset="50%" stop-color="#70a5fd" stop-opacity="0.2">
      <animate attributeName="stop-opacity" values="0.1;0.35;0.1" dur="4s" repeatCount="indefinite" />
    </stop>
    <stop offset="100%" stop-color="#0d1117" stop-opacity="0.0" />
  </linearGradient>

  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="3" result="blur" />
    <feMerge>
      <feMergeNode in="blur" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>

  <filter id="glow-strong" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="6" result="blur" />
    <feMerge>
      <feMergeNode in="blur" />
      <feMergeNode in="blur" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>
</defs>
"""
    svg = svg.replace("<style>", defs_block + "\n<style>")
    svg = re.sub(r'class="ct-area"', 'class="ct-area" fill="url(#animatedAreaGrad)"', svg)

    # Animate line
    line_anim = """
  <animate attributeName="stroke-dashoffset"
           values="5000;0;0;5000"
           keyTimes="0;0.45;0.85;1"
           dur="8s"
           repeatCount="indefinite" />
  <animate attributeName="stroke-width"
           values="3;4.2;3"
           dur="3s"
           repeatCount="indefinite" />
"""
    svg = re.sub(r'(<path[^>]*class="ct-line"[^>]*)>', r'\1 filter="url(#glow)">\n' + line_anim, svg)

    # Animate points
    point_anim = """
    <animate attributeName="stroke-width"
             values="6;10;6"
             dur="2.5s"
             repeatCount="indefinite" />
    <animate attributeName="stroke-opacity"
             values="0.7;1;0.7"
             dur="2.5s"
             repeatCount="indefinite" />
"""
    svg = re.sub(r'(<line[^>]*class="ct-point"[^>]*>)(\s*</line>)', r"\1\n" + point_anim + r"\2", svg)

    # Traveling particle
    if line_path_d:
        particle = f"""
    <g filter="url(#glow-strong)">
      <circle r="5" fill="#ffffff" stroke="#38bdae" stroke-width="2.5">
        <animateMotion path="{line_path_d}"
                       dur="8s"
                       repeatCount="indefinite"
                       keyPoints="0;0.45;0.85;1"
                       keyTimes="0;0.45;0.85;1"
                       calcMode="linear" />
      </circle>
    </g>
"""
        pos = svg.rfind("</svg>")
        svg = svg[:pos] + particle + svg[pos:]

    out_path = os.path.join(os.path.dirname(__file__), "..", "github-metrics", "activity-graph.svg")
    out_path = os.path.abspath(out_path)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print("Updated animated activity graph at:", out_path)

if __name__ == "__main__":
    update_activity_graph()
