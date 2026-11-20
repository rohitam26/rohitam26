#!/usr/bin/env python3
import sys
import os
import re
import urllib.request

def fetch_base_svg():
    url = "https://github-readme-activity-graph.ashutosh-dwivedi0710.workers.dev/graph?username=rohitam26&theme=tokyo-night&bg_color=0d1117&color=70a5fd&line=bf91f3&point=38bdae&area=true&hide_border=true&custom_title=Rohita%20Muthu's%20Activity%20Graph"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        print(f"Fallback URL due to: {e}")
        mirror_url = "https://github-readme-activity-graph.vercel.app/graph?username=rohitam26&theme=tokyo-night&bg_color=0d1117&color=70a5fd&line=bf91f3&point=38bdae&area=true&hide_border=true&custom_title=Rohita%20Muthu's%20Activity%20Graph"
        req_fallback = urllib.request.Request(
            mirror_url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        )
        with urllib.request.urlopen(req_fallback, timeout=15) as resp:
            return resp.read().decode('utf-8')

def get_line_path(svg):
    m = re.search(r'<path[^>]*class="ct-line"[^>]*d="([^"]+)"', svg)
    if not m:
        m = re.search(r'<path[^>]*d="([^"]+)"[^>]*class="ct-line"', svg)
    return m.group(1) if m else ""

def generate_variants(base_svg, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    line_path = get_line_path(base_svg)

    # 1. Base Styles & Filters
    common_defs = """<defs>
  <linearGradient id="areaGradBase" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#bf91f3" stop-opacity="0.45" />
    <stop offset="50%" stop-color="#581c87" stop-opacity="0.2" />
    <stop offset="100%" stop-color="#0d1117" stop-opacity="0.0" />
  </linearGradient>

  <linearGradient id="auroraGrad" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#bf91f3" stop-opacity="0.55">
      <animate attributeName="stop-color" values="#bf91f3;#38bdf8;#34d399;#f472b6;#bf91f3" dur="8s" repeatCount="indefinite" />
      <animate attributeName="stop-opacity" values="0.35;0.7;0.35" dur="3s" repeatCount="indefinite" />
    </stop>
    <stop offset="50%" stop-color="#581c87" stop-opacity="0.25">
      <animate attributeName="stop-color" values="#581c87;#1e3a8a;#065f46;#831843;#581c87" dur="8s" repeatCount="indefinite" />
    </stop>
    <stop offset="100%" stop-color="#0d1117" stop-opacity="0.0" />
  </linearGradient>

  <linearGradient id="radarBeamGrad" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#38bdf8" stop-opacity="0" />
    <stop offset="50%" stop-color="#38bdf8" stop-opacity="0.25" />
    <stop offset="100%" stop-color="#38bdf8" stop-opacity="0" />
  </linearGradient>

  <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="3.5" result="blur" />
    <feMerge>
      <feMergeNode in="blur" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>
</defs>"""

    # Helper to inject defs
    def inject_defs(svg, defs):
        return re.sub(r'(<svg[^>]*>)', r'\1\n' + defs, svg, count=1)

    # Base point animation
    point_anim = (
        '<animate attributeName="stroke-width" values="6;13;6" dur="1.8s" repeatCount="indefinite" />'
        '<animate attributeName="stroke-opacity" values="0.6;1;0.6" dur="1.8s" repeatCount="indefinite" />'
    )

    # Standard styling
    base_css = """
    .ct-series-a .ct-area {
      fill: url(#areaGradBase) !important;
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

    # -------------------------------------------------------------
    # VARIANT 1: 🌠 RIDING COMET PARTICLE (animateMotion along path)
    # -------------------------------------------------------------
    v1 = inject_defs(base_svg, common_defs)
    v1 = v1.replace('</style>', base_css + '\n</style>')
    v1 = re.sub(r'(<line[^>]*?class="ct-point"[^>]*?>)(</line>)', r'\g<1>' + point_anim + r'\g<2>', v1)
    
    comet_elem = f"""<g>
  <!-- Comet Particle Riding Along Contour -->
  <g>
    <!-- Outer Cyan Aura -->
    <circle r="12" fill="#38bdf8" opacity="0.3" filter="drop-shadow(0 0 10px #38bdf8)">
      <animate attributeName="r" values="8;14;8" dur="1.2s" repeatCount="indefinite" />
      <animate attributeName="opacity" values="0.2;0.5;0.2" dur="1.2s" repeatCount="indefinite" />
    </circle>
    <!-- Core Purple Glow -->
    <circle r="6" fill="#c084fc" filter="drop-shadow(0 0 6px #c084fc)" />
    <!-- Center Pure White Star Core -->
    <circle r="3" fill="#ffffff" />
    <animateMotion path="{line_path}" dur="4s" repeatCount="indefinite" rotate="auto" />
  </g>
</g>"""
    v1 = v1.replace('</svg>', comet_elem + '\n</svg>')
    with open(os.path.join(out_dir, "activity-graph-comet.svg"), "w", encoding="utf-8") as f:
        f.write(v1)

    # -------------------------------------------------------------
    # VARIANT 2: 📡 HOLOGRAPHIC RADAR SCANNER BEAM
    # -------------------------------------------------------------
    v2 = inject_defs(base_svg, common_defs)
    v2 = v2.replace('</style>', base_css + '\n</style>')
    v2 = re.sub(r'(<line[^>]*?class="ct-point"[^>]*?>)(</line>)', r'\g<1>' + point_anim + r'\g<2>', v2)

    radar_elem = """<g>
  <!-- Sweeping Radar Beam -->
  <rect y="80" width="60" height="270" fill="url(#radarBeamGrad)">
    <animate attributeName="x" from="60" to="1120" dur="3.5s" repeatCount="indefinite" />
  </rect>
  <!-- Vertical Laser Line -->
  <line y1="80" y2="350" stroke="#38bdf8" stroke-width="2" filter="drop-shadow(0 0 8px #38bdf8)">
    <animate attributeName="x1" from="90" to="1150" dur="3.5s" repeatCount="indefinite" />
    <animate attributeName="x2" from="90" to="1150" dur="3.5s" repeatCount="indefinite" />
    <animate attributeName="stroke-opacity" values="0.7;1;0.7" dur="1s" repeatCount="indefinite" />
  </line>
</g>"""
    v2 = v2.replace('</svg>', radar_elem + '\n</svg>')
    with open(os.path.join(out_dir, "activity-graph-radar.svg"), "w", encoding="utf-8") as f:
        f.write(v2)

    # -------------------------------------------------------------
    # VARIANT 3: 🌌 AURORA BOREALIS SHIFTING LIQUID GRADIENT
    # -------------------------------------------------------------
    v3 = inject_defs(base_svg, common_defs)
    aurora_css = base_css.replace('url(#areaGradBase)', 'url(#auroraGrad)')
    v3 = v3.replace('</style>', aurora_css + '\n</style>')
    v3 = re.sub(r'(<line[^>]*?class="ct-point"[^>]*?>)(</line>)', r'\g<1>' + point_anim + r'\g<2>', v3)
    
    # Breathing line color shift
    line_aurora_anim = (
        '>'
        '<animate attributeName="stroke" values="#bf91f3;#38bdf8;#34d399;#f472b6;#bf91f3" dur="8s" repeatCount="indefinite" />'
        '<animate attributeName="stroke-width" values="3.2;4.2;3.2" dur="2s" repeatCount="indefinite" />'
    )
    v3 = re.sub(r'(<path[^>]*?class="ct-line"[^>]*?)>', r'\g<1>' + line_aurora_anim, v3)
    with open(os.path.join(out_dir, "activity-graph-aurora.svg"), "w", encoding="utf-8") as f:
        f.write(v3)

    # -------------------------------------------------------------
    # VARIANT 4: 👑 PEAK MILESTONE TWINKLING SPARKLES (✦)
    # -------------------------------------------------------------
    v4 = inject_defs(base_svg, common_defs)
    v4 = v4.replace('</style>', base_css + '\n</style>')
    v4 = re.sub(r'(<line[^>]*?class="ct-point"[^>]*?>)(</line>)', r'\g<1>' + point_anim + r'\g<2>', v4)

    # Peak coordinates in rohitam26 graph:
    # Day 21 (x=90, y=83.375) - max peak (80 contributions)
    # Day 15 (x=938, y=173) - secondary spike (52 contributions)
    sparkles = """<g>
  <!-- Peak 1 Star Sparkle (Day 21 - Max Peak) -->
  <g transform="translate(90, 68)">
    <path d="M 0 -10 L 2.5 -2.5 L 10 0 L 2.5 2.5 L 0 10 L -2.5 2.5 L -10 0 L -2.5 -2.5 Z" fill="#ffd700" filter="drop-shadow(0 0 8px #ffd700)">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="3s" repeatCount="indefinite" />
      <animate attributeName="opacity" values="0.4;1;0.4" dur="1.5s" repeatCount="indefinite" />
    </path>
    <circle r="2" fill="#ffffff" />
  </g>

  <!-- Peak 2 Star Sparkle (Day 15 - Second Peak) -->
  <g transform="translate(938, 155)">
    <path d="M 0 -8 L 2 -2 L 8 0 L 2 2 L 0 8 L -2 2 L -8 0 L -2 -2 Z" fill="#38bdf8" filter="drop-shadow(0 0 6px #38bdf8)">
      <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="3.5s" repeatCount="indefinite" />
      <animate attributeName="opacity" values="0.3;0.9;0.3" dur="1.8s" repeatCount="indefinite" />
    </path>
    <circle r="1.5" fill="#ffffff" />
  </g>

  <!-- Peak 3 Star Sparkle (Day 25 - Third Peak at x=231, y=245) -->
  <g transform="translate(231.33, 230)">
    <path d="M 0 -6 L 1.5 -1.5 L 6 0 L 1.5 1.5 L 0 6 L -1.5 1.5 L -6 0 L -1.5 -1.5 Z" fill="#c084fc" filter="drop-shadow(0 0 5px #c084fc)">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="4s" repeatCount="indefinite" />
      <animate attributeName="opacity" values="0.3;1;0.3" dur="1.2s" repeatCount="indefinite" />
    </path>
  </g>
</g>"""
    v4 = v4.replace('</svg>', sparkles + '\n</svg>')
    with open(os.path.join(out_dir, "activity-graph-peaks.svg"), "w", encoding="utf-8") as f:
        f.write(v4)

    # -------------------------------------------------------------
    # VARIANT 5: 🌐 CYBERPUNK MATRIX HOLOGRAPHIC GRID
    # -------------------------------------------------------------
    v5 = inject_defs(base_svg, common_defs)
    grid_css = base_css + """
    .ct-grid.ct-horizontal {
      stroke: #38bdf8 !important;
      stroke-dasharray: 4, 8 !important;
      opacity: 0.35 !important;
    }
    .ct-grid.ct-vertical {
      stroke: #bf91f3 !important;
      stroke-dasharray: 4, 8 !important;
      opacity: 0.3 !important;
    }
    """
    v5 = v5.replace('</style>', grid_css + '\n</style>')
    v5 = re.sub(r'(<line[^>]*?class="ct-grid ct-horizontal"[^>]*?)>', r'\g<1>><animate attributeName="stroke-dashoffset" from="0" to="24" dur="2s" repeatCount="indefinite" /></line>', v5)
    v5 = re.sub(r'(<line[^>]*?class="ct-point"[^>]*?>)(</line>)', r'\g<1>' + point_anim + r'\g<2>', v5)
    with open(os.path.join(out_dir, "activity-graph-grid.svg"), "w", encoding="utf-8") as f:
        f.write(v5)

    # -------------------------------------------------------------
    # VARIANT 6: ⚡ THE ULTIMATE FUSION (ALL EFFECTS COMBINED)
    # -------------------------------------------------------------
    v6 = inject_defs(base_svg, common_defs)
    fusion_css = base_css.replace('url(#areaGradBase)', 'url(#auroraGrad)') + """
    .ct-series-a .ct-line {
      stroke: #bf91f3 !important;
      stroke-width: 3.5px !important;
      filter: drop-shadow(0 0 6px rgba(191, 145, 243, 0.9)) !important;
    }
    """
    v6 = v6.replace('</style>', fusion_css + '\n</style>')
    v6 = re.sub(r'(<line[^>]*?class="ct-point"[^>]*?>)(</line>)', r'\g<1>' + point_anim + r'\g<2>', v6)

    # Traveling laser dashes on line
    line_laser = (
        ' stroke-dasharray="24, 12, 6, 12"'
        '>'
        '<animate attributeName="stroke-dashoffset" from="0" to="-108" dur="2s" repeatCount="indefinite" />'
        '<animate attributeName="stroke-width" values="3.2;4.2;3.2" dur="2s" repeatCount="indefinite" />'
    )
    v6 = re.sub(r'(<path[^>]*?class="ct-line"[^>]*?)>', r'\g<1>' + line_laser, v6)

    # Add Radar Beam + Comet Particle + Peak Sparkles all together!
    fusion_elements = f"""<g>
  <!-- 1. Holographic Radar Scanner Beam -->
  <rect y="80" width="50" height="270" fill="url(#radarBeamGrad)">
    <animate attributeName="x" from="60" to="1120" dur="4s" repeatCount="indefinite" />
  </rect>
  <line y1="80" y2="350" stroke="#38bdf8" stroke-width="2" filter="drop-shadow(0 0 8px #38bdf8)">
    <animate attributeName="x1" from="90" to="1150" dur="4s" repeatCount="indefinite" />
    <animate attributeName="x2" from="90" to="1150" dur="4s" repeatCount="indefinite" />
    <animate attributeName="stroke-opacity" values="0.7;1;0.7" dur="1s" repeatCount="indefinite" />
  </line>

  <!-- 2. Peak Milestone Sparkles -->
  {sparkles}

  <!-- 3. Comet Star Riding Path -->
  {comet_elem}
</g>"""
    v6 = v6.replace('</svg>', fusion_elements + '\n</svg>')
    with open(os.path.join(out_dir, "activity-graph-fusion.svg"), "w", encoding="utf-8") as f:
        f.write(v6)
    
    # Also save fusion as the main activity-graph.svg default
    with open(os.path.join(out_dir, "activity-graph.svg"), "w", encoding="utf-8") as f:
        f.write(v6)

    print("All 6 Animation Variants generated successfully in", out_dir)

if __name__ == '__main__':
    base = fetch_base_svg()
    out = sys.argv[1] if len(sys.argv) > 1 else "dist"
    generate_variants(base, out)
