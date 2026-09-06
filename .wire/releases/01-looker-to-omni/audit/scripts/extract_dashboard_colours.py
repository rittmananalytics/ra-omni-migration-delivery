"""Extract colour and font usage from the three in-scope dashboards' raw API payloads, to derive the Omni dashboard theme."""
import collections
import json
import re

hexes = collections.Counter()
fonts = collections.Counter()
text_colors = collections.Counter()
for did in ("267", "416", "255"):
    d = json.load(open(".wire/releases/01-looker-to-omni/audit/raw/dashboard_%s.json" % did))
    s = json.dumps(d)
    for m in re.findall(r"#[0-9a-fA-F]{6}\b", s):
        hexes[m.lower()] += 1
    for e in d.get("dashboard_elements") or []:
        for vc in ((e.get("result_maker") or {}).get("vis_config") or {}, (e.get("query") or {}).get("vis_config") or {}):
            if vc.get("text_color"):
                text_colors[vc["text_color"]] += 1
            if vc.get("font_family"):
                fonts[vc["font_family"]] += 1
    print(did, "appearance:", d.get("appearance"), "background:", d.get("background_color"), "title_color:", d.get("title_color"),
          "text_tile_text_color:", d.get("text_tile_text_color"), "tile_bg:", d.get("tile_background_color"), "tile_text:", d.get("tile_text_color"))
print("top hex colours:", hexes.most_common(20))
print("text colours:", text_colors.most_common(5), "fonts:", fonts.most_common(5))
