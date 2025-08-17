# sanitize_import.py — works with klayout -b -r or plain Python (klayout.db)
# Usage (example):
#   klayout -b -r sanitize_import.py \
#     -rd SRC=swsources16.gds -rd TGT=target.gds -rd OUT=target_with_src.gds -rd TOPNAME=SW_SOURCES16

import os, sys
try:
    from klayout import db as pya
except Exception:
    import pya  # if running inside KLayout’s Python

def parse_rd_args(argv):
    out = {}
    for i, a in enumerate(argv):
        if a == "-rd" and i+1 < len(argv):
            kv = argv[i+1]
            if "=" in kv:
                k, v = kv.split("=", 1)
                out[k] = v
    return out

rd = parse_rd_args(sys.argv)
SRC     = rd.get("SRC",     os.environ.get("SRC",     "swcascsrc_playground.gds"))
TGT     = rd.get("TGT",     os.environ.get("TGT",     "target.gds"))
OUT     = rd.get("OUT",     os.environ.get("OUT",     "target_merged.gds"))
TOPNAME = rd.get("TOPNAME", os.environ.get("TOPNAME", "SWCASCSRC"))

# --- load layouts ---
sly = pya.Layout(); sly.read(SRC)
tly = pya.Layout()
if os.path.exists(TGT):
    tly.read(TGT)
else:
    tly.dbu = sly.dbu
ttop = tly.top_cell() or tly.create_cell("TOP")

# --- fix reserved context cell name if present ---
for c in sly.each_cell():
    if c.name == "$$$CONTEXT_INFO$$$":
        c.name = "__CONTEXT_INFO__"

# --- expand fragile 1-D AREFs (rows=1 xor cols=1) into SREFs ---
def explode_1d_arefs(cell):
    to_delete = []
    for inst in cell.each_inst():
        if inst.is_regular_array():
            ca = inst
            cols, rows = ca.na.x, ca.na.y
            if (cols == 1) ^ (rows == 1):
                for cx in range(cols):
                    for ry in range(rows):
                        t = pya.Trans(ca.trans) * pya.Trans(ca.a * cx + ca.b * ry)
                        cell.insert(pya.CellInstArray(ca.cell_index(), t))
                to_delete.append(ca)
    for ca in to_delete:
        cell.erase(ca)

for c in sly.each_cell():
    explode_1d_arefs(c)

# --- create a destination cell and copy the full tree into it ---
src_top = sly.top_cell()
dst_root = tly.create_cell(TOPNAME or src_top.name)
dst_root.copy_tree(src_top)  # <-- correct API: Cell.copy_tree(Cell) (cross-layout) :contentReference[oaicite:1]{index=1}

# place one instance at origin (optional—comment out if you just want the copied cell)
ttop.insert(pya.CellInstArray(dst_root.cell_index(), pya.Trans()))

tly.write(OUT)
print(f"Wrote {OUT}")

