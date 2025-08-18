# gds_ld1_to_ld2_inplace.py
# Run: klayout -b -r gds_ld1_to_ld2_inplace.py -rd SRC=in.gds -rd OUT=out.gds
import sys, os
try:
    from klayout import db as pya
except:
    import pya

def rd(k, d=None):
    a=sys.argv
    return next((a[i+1].split("=",1)[1] for i,x in enumerate(a) if x=="-rd" and a[i+1].startswith(k+"=")), os.environ.get(k,d))

SRC = rd("SRC","swcascsrc_playground.gds")
OUT = rd("OUT","swcasc.gds")

ly = pya.Layout(); ly.read(SRC)

# move ALL shapes on (L,1) -> (L,2); keep arrays; no new cells
layers = {ly.get_info(li).layer for li in ly.layer_indexes() if ly.get_info(li).datatype == 1}
for L in layers:
    s_li = ly.find_layer(pya.LayerInfo(L,1))
    if s_li < 0: continue
    d_li = ly.layer(pya.LayerInfo(L,2))
    for c in ly.each_cell():
        shs = c.shapes(s_li)
        if shs.is_empty(): continue
        tmp = [s for s in shs.each()]
        for s in tmp: c.shapes(d_li).insert(s)
        shs.clear()

# write plain GDS (no PCell/library context) — exports directly, not embedded
opt = pya.SaveLayoutOptions(); opt.write_context_info = False
ly.write(OUT, opt)
print("Wrote", OUT)

