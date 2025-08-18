# promote_text_to_pin.py
# Purpose:
#   - Load a source GDS (default: swcascsrc_playground.gds)
#   - Sanitize: rename $$$CONTEXT_INFO$$$, explode 1-D AREFs
#   - Copy hierarchy into a NEW layout (no library/proxy)
#   - Remap TEXT shapes from "label" layers to "pin" layers
#   - Write a clean GDS with the same top cell as the source (or a custom name)
#
# Run examples:
#   klayout -b -r promote_text_to_pin.py
#   klayout -b -r promote_text_to_pin.py -rd SRC=foo.gds -rd OUT=foo_pins.gds
#   klayout -b -r promote_text_to_pin.py -rd MAP="5/0:67/44,8/0:68/44"
#   klayout -b -r promote_text_to_pin.py -rd ALL_TO="67/44"
#   (env vars also work: SRC=..., OUT=..., MAP=..., ALL_TO=..., TOPNAME=...)

import os, sys
try:
    from klayout import db as pya
except Exception:
    import pya  # if running inside KLayout’s Python

def parse_rd_args(argv):
    """Parse -rd KEY=VALUE pairs from argv."""
    out = {}
    for i, a in enumerate(argv):
        if a == "-rd" and i + 1 < len(argv):
            kv = argv[i + 1]
            if "=" in kv:
                k, v = kv.split("=", 1)
                out[k] = v
    return out

def parse_layer_pair(s):
    """Parse 'L/D' -> (L, D) as ints."""
    l, d = s.split("/")
    return int(l), int(d)

def parse_map(map_str):
    """
    Parse mapping string like:
      "5/0:67/44,8/0:68/44"
    into { (5,0): (67,44), (8,0): (68,44) }
    """
    m = {}
    if not map_str:
        return m
    for item in map_str.split(","):
        item = item.strip()
        if not item:
            continue
        src, dst = item.split(":")
        m[parse_layer_pair(src)] = parse_layer_pair(dst)
    return m

# ---- config from -rd or environment or defaults ----
rd = parse_rd_args(sys.argv)
SRC     = rd.get("SRC",     os.environ.get("SRC",     "swcascsrc_playground.gds"))
OUT     = rd.get("OUT",     os.environ.get("OUT",     "swcascsrc_playground_pins.gds"))
TOPNAME = rd.get("TOPNAME", os.environ.get("TOPNAME", None))
MAP     = parse_map(rd.get("MAP", os.environ.get("MAP", "")))  # explicit per-layer map
ALL_TO  = rd.get("ALL_TO",  os.environ.get("ALL_TO",  ""))     # override: send ALL TEXT to this one layer (L/D)
ALL_TO_PAIR = parse_layer_pair(ALL_TO) if ALL_TO else None

# ---- read source layout ----
sly = pya.Layout()
sly.read(SRC)
src_top = sly.top_cell()

# ---- sanitize: rename reserved cell; explode 1-D arrays ----
for c in sly.each_cell():
    if c.name == "$$$CONTEXT_INFO$$$":
        c.name = "__CONTEXT_INFO__"

def explode_1d_arefs(cell):
    to_del = []
    for inst in cell.each_inst():
        if inst.is_regular_array():
            ca = inst
            cols, rows = ca.na.x, ca.na.y
            # exactly one dimension is 1 (1D array) → expand to SREFs
            if (cols == 1) ^ (rows == 1):
                for cx in range(cols):
                    for ry in range(rows):
                        t = pya.Trans(ca.trans) * pya.Trans(ca.a * cx + ca.b * ry)
                        cell.insert(pya.CellInstArray(ca.cell_index(), t))
                to_del.append(ca)
    for ca in to_del:
        cell.erase(ca)

for c in sly.each_cell():
    explode_1d_arefs(c)

# ---- create NEW destination layout and copy hierarchy ----
dly = pya.Layout()
dly.dbu = sly.dbu

# 1:1 layer mapping for shapes/copies
layer_map = {}
for s_li in sly.layer_indexes():
    layer_map[s_li] = dly.layer(sly.get_info(s_li))

dst_top = dly.create_cell(TOPNAME or src_top.name)
dst_top.copy_tree(src_top)  # copies hierarchy cross-layout into dly

# ---- build lookup for layer indices based on (L,D) pairs in destination ----
def li_of(pair):
    return dly.layer(pya.LayerInfo(pair[0], pair[1]))

# ---- collect all TEXT layer pairs present (for info) ----
text_layers_present = set()
for c in dly.each_cell():
    for sh in c.shapes_iter():
        if sh.is_text():
            info = dly.get_info(sh.layer)
            text_layers_present.add((info.layer, info.dtype))

# ---- move TEXT from label layers to pin layers ----
# Strategy:
#   * If ALL_TO is given: every TEXT goes to that single target layer.
#   * Else if MAP has an entry for the TEXT's (L/D), move to that mapped (L/D).
#   * Else leave it where it is (no guesswork).
moved = 0
for c in dly.each_cell():
    # We'll collect new texts to avoid mutating in-place while iterating
    new_texts = []
    to_delete = []
    for it in c.shapes_iter():
        if not it.is_text():
            continue
        text = it.text  # pya.Text
        src_li = it.layer
        src_info = dly.get_info(src_li)
        src_pair = (src_info.layer, src_info.dtype)

        if ALL_TO_PAIR:
            dst_li = li_of(ALL_TO_PAIR)
        elif src_pair in MAP:
            dst_li = li_of(MAP[src_pair])
        else:
            continue  # no mapping rule: keep as-is

        new_texts.append((dst_li, pya.Text(text.string, text.trans, text.size)))
        to_delete.append(it)

    # insert new texts then remove old ones
    for dst_li, t in new_texts:
        c.shapes(dst_li).insert(t)
        moved += 1
    for it in to_delete:
        c.shapes(it.layer).erase(it)

# ---- write output as its own top-level layout ----
dly.write(OUT)

# ---- print a small report ----
print(f"Source: {SRC}")
print(f"Output: {OUT}")
print(f"DBU: {dly.dbu}")
print(f"Top cell: {dst_top.name}")
if text_layers_present:
    print("TEXT layers seen in source (L/D):", ", ".join(f"{l}/{d}" for l,d in sorted(text_layers_present)))
else:
    print("No TEXT layers found.")
if ALL_TO_PAIR:
    print(f"All TEXT moved to: {ALL_TO_PAIR[0]}/{ALL_TO_PAIR[1]}")
else:
    print("Mapped TEXT layers:", ", ".join(f"{sl}/{sd}->{dl}/{dd}"
          for (sl,sd),(dl,dd) in sorted(MAP.items()))) if MAP else print("No TEXT mapping provided; TEXT left unchanged where no rule applied.")
print(f"TEXT moved: {moved}")

