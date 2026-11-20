#!/usr/bin/env python3
import sys
import os
import re
import urllib.request

def fetch_and_animate_activity(out_paths):
    # Fetch with Rohita's signature purple line (#bf91f3) and teal points (#38bdae)
    url = "https://github-readme-activity-graph.ashutosh-dwivedi0710.workers.dev/graph?username=rohitam26&theme=tokyo-night&bg_color=0d1117&color=70a5fd&line=bf91f3&point=38bdae&area=true&hide_border=true&custom_title=Rohita%20Muthu's%20Activity%20Graph"
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            svg = resp.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching from primary URL: {e}")
        mirror_url = "https://github-readme-activity-graph.vercel.app/graph?username=rohitam26&theme=tokyo-night&bg_color=0d1117&color=70a5fd&line=bf91f3&point=38bdae&area=true&hide_border=true&custom_title=Rohita%20Muthu's%20Activity%20Graph"
        req_fallback = urllib.request.Request(
            mirror_url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        )
        with urllib.request.urlopen(req_fallback, timeout=15) as resp:
            svg = resp.read().decode('utf-8')

    # Add animated defs matching Rohita's purple & teal palette
    defs = """<defs>
  <linearGradient id="animatedAreaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#bf91f3" stop-opacity="0.45">
      <animate attributeName="stop-opacity" values="0.15;0.5;0.15" dur="3s" repeatCount="indefinite" />
    </stop>
    <stop offset="50%" stop-color="#581c87" stop-opacity="0.2">
      <animate attributeName="stop-opacity" values="0.1;0.35;0.1" dur="3s" repeatCount="indefinite" />
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
</defs>"""

    # Inject defs right after <svg ...>
    svg = re.sub(r'(<svg[^>]*>)', r'\1\n' + defs, svg, count=1)

    # Style updates for active traveling pulse
    css_animation = """
    .ct-series-a .ct-area {
      fill: url(#animatedAreaGrad) !important;
    }
    .ct-series-a .ct-line {
      stroke: #bf91f3 !important;
      stroke-width: 3.5px !important;
      filter: drop-shadow(0 0 5px rgba(191, 145, 243, 0.8)) !important;
      stroke-linecap: round !important;
      stroke-linejoin: round !important;
    }
    .ct-series-a .ct-point {
      stroke: #38bdae !important;
      fill: #ffffff !important;
      filter: drop-shadow(0 0 4px #38bdae) !important;
    }
    """
    svg = svg.replace('</style>', css_animation + '\n</style>')

    # Inject continuous traveling laser pulse animation into .ct-line
    line_anim = (
        ' stroke-dasharray="24, 12, 6, 12"'
        '>'
        '<animate attributeName="stroke-dashoffset" from="0" to="-108" dur="2s" repeatCount="indefinite" />'
        '<animate attributeName="stroke-width" values="3.2;4.2;3.2" dur="2s" repeatCount="indefinite" />'
    )
    svg = re.sub(r'(<path[^>]*?class="ct-line"[^>]*?)>', r'\g<1>' + line_anim, svg)

    # Inject pulsing radius/stroke-width on every data point (.ct-point)
    point_anim = (
        '<animate attributeName="stroke-width" values="6;13;6" dur="1.8s" repeatCount="indefinite" />'
        '<animate attributeName="stroke-opacity" values="0.6;1;0.6" dur="1.8s" repeatCount="indefinite" />'
    )
    svg = re.sub(r'(<line[^>]*?class="ct-point"[^>]*?>)(</line>)', r'\g<1>' + point_anim + r'\g<2>', svg)

    for path in out_paths:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg)
        print(f"Saved animated activity graph to {path} ({len(svg)} bytes)")

if __name__ == '__main__':
    targets = sys.argv[1:] if len(sys.argv) > 1 else ["dist/activity-graph.svg"]
    fetch_and_animate_activity(targets)
