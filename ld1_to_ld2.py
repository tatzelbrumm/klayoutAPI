# ld1_to_ld2.py
# Convert all layers with D=1 to the same layer number with D=2, stand-alone output.
# Usage examples:
#   klayout -b -r ld1_to_ld2.py
#   klayout -b -r ld1_to_ld2.py -rd SRC=swcascsrc_playground.gds -rd OUT=out.gds -rd TOPNAME=MYTOP
#   SRC=foo.gds OUT=foo_ld2.gds klayout -b -r ld1_to_ld2.py

import os, sys
try:
    from klayout import db as pya
except Exception:
    import pya  # if running inside KLayout's Python

def parse_rd_args(argv):
    out = {}
    for i, a in enumerate(argv):
        if a == "-rd" and i + 1 < len(argv):
            kv = argv[i + 1]
            if "=" in kv:
                k, v = kv.split("=", 1)
                out[k] = v
    return out

rd = parse_rd_args(sys.argv)
SRC     = rd.get("SRC",     os.environ.get("SRC",     "swcascsrc_playground.gds"))
OUT     = rd.get("OUT",     os.environ.get("OUT",     "swcascsrc_playground_ld2.gds"))
TOPNAME = rd.get("TOPNAME", os.environ.get("TOPNAME"))  # optional: rename top cell

# --- read source ---
sly = pya.Layout()
sly.read(SRC)
src_top = sly.top_cell()

# --- build destination layout (stand-alone copy) ---
dly = pya.Layout()
dly.dbu = sly.dbu

# copy hierarchy into a NEW layout (no embedding)
dst_top = dly.create_cell(TOPNAME or src_top.name)
dst_top.copy_tree(src_top)   # Cell.copy_tree works across layouts

# --- convert all (L,1) -> (L,2) in the destination ---
# Collect all layer numbers that have dtype 1
ld1_pairs = []
for li in dly.layer_indexes():
    info = dly.get_info(li)
    if info.dtype == 1:
        ld1_pairs.append(info.layer)

# For each such layer number, move shapes from D=1 to D=2
for L in ld1_pairs:
    src_li = dly.find_layer(pya.LayerInfo(L, 1))
    if src_li < 0:
        continue
    dst_li = dly.layer(pya.LayerInfo(L, 2))
    for c in dly.each_cell():
        src_shapes = c.shapes(src_li)
        if src_shapes.is_empty():
            continue
        # Copy all shapes (BOUNDARY, PATH, TEXT, etc.) to the destination layer
        # Make a list first to avoid modifying while iterating
        to_copy = [s for s in src_shapes.each()]
        for s in to_copy:
            c.shapes(dst_li).insert(s)
        src_shapes.clear()  # remove originals from D=1

# --- write stand-alone output ---
dly.write(OUT)
print(f"Converted all (L,1) -> (L,2) and wrote: {OUT}")

