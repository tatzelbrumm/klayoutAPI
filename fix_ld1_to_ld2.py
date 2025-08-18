# gds_fix_ld1_to_ld2.py
# Usage:
#   klayout -b -r gds_fix_ld1_to_ld2.py -rd SRC=in.gds -rd OUT=out.gds -rd TOP=OptionalTopName
import sys, os
try:
    from klayout import db as pya
except:
    import pya

# read -rd args
def rd(k, d=None):
    a=sys.argv
    return next((a[i+1].split("=",1)[1] for i,x in enumerate(a) if x=="-rd" and a[i+1].startswith(k+"=")), os.environ.get(k,d))

SRC = rd("SRC","swcascsrc_playground.gds")
OUT = rd("OUT","out.gds")
TOP = rd("TOP",None)

# read source
s = pya.Layout(); s.read(SRC)
stop = s.top_cell()

# copy to a NEW layout (keeps arrays; no embedding)
d = pya.Layout(); d.dbu = s.dbu
dst = d.create_cell(TOP or stop.name)
dst.copy_tree(stop)               # real cells (no PCells/proxies)

# remap all (L,1) -> (L,2) for ALL shapes
ld1 = {d.get_info(li).layer for li in d.layer_indexes() if d.get_info(li).datatype == 1}
for L in ld1:
    src_li = d.find_layer(pya.LayerInfo(L,1))
    if src_li < 0: continue
    dst_li = d.layer(pya.LayerInfo(L,2))
    for c in d.each_cell():
        shs = c.shapes(src_li)
        if shs.is_empty(): continue
        buf = [sh for sh in shs.each()]     # clone list, then move
        for sh in buf:
            c.shapes(dst_li).insert(sh)     # insert same geometry on new (L,2)
        shs.clear()                          # drop old (L,1)

# write standalone GDS with no PCell/library context
opt = pya.SaveLayoutOptions(); opt.write_context_info = False
d.write(OUT, opt)
print(f"Wrote {OUT}")

