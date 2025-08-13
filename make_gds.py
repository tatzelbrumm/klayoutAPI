# make_gds.py
import pya

# Create layout
layout = pya.Layout()
layout.dbu = 0.001  # 1 nm units
top = layout.create_cell("SWITCHED_PMOS_CASCODE")

# Layers
l_active = layout.layer(pya.LayerInfo(1, 0))
l_po     = layout.layer(pya.LayerInfo(5, 0))
l_co     = layout.layer(pya.LayerInfo(6, 0))
l_m1     = layout.layer(pya.LayerInfo(8, 0))
l_pimp   = layout.layer(pya.LayerInfo(14, 0))
l_nwell  = layout.layer(pya.LayerInfo(31, 0))

# Draw shapes
top.shapes(l_active).insert(pya.Box(290, -380, 440, 380))
top.shapes(l_po).insert(    pya.Box(-150, -150, 620, 150))
top.shapes(l_co).insert(    pya.Box(-80,  -80,   80,  80))
top.shapes(l_m1).insert(    pya.Box(-80, -130,   80, 130))
top.shapes(l_pimp).insert(  pya.Box(-10, -560,  740, 560))
top.shapes(l_nwell).insert( pya.Box(-30, -790,  760, 790))

# Save GDS
layout.write("switched_pmos_cascode.gds")
print("Wrote switched_pmos_cascode.gds")

