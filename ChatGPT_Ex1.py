import klayout.db as pya

# 1) Read the GDS
layout = pya.Layout()
layout.read("pcascsrc.gds")

# 2) Grab your top-level cell (only one in this file)
cell = layout.top_cell()

# 3) Get the layer‐index table and the corresponding LayerInfo objects
layer_idxs  = layout.layer_indexes()   # e.g. [0, 1, …]
layer_infos = layout.layer_infos()     # list of pya.LayerInfo matching those indexes

# 4) Iterate each registered layer and dump any polygons
for idx, info in zip(layer_idxs, layer_infos):
    layer_no, datatype = info.layer, info.datatype
    shapes = cell.shapes(idx)
    for i, shape in enumerate(shapes.each()):
        if shape.is_polygon():
            poly = shape.polygon              # a pya.Polygon
            pts  = [(pt.x, pt.y) for pt in poly.each_point()]
            print(f"Layer {layer_no}, DType {datatype}, Polygon #{i}:")
            print(f"  {len(pts)} points → {pts}")
