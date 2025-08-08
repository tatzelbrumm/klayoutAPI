import klayout.db as pya

# 1) Create a Layout object and read your GDS
layout = pya.Layout()
layout.read("pcascsrc.gds")

# 2) Get the top cell (if you know the name, you can also do layout.cell("pcascsrc"))
cell = layout.top_cell()

# 3) Iterate over all layers present in that cell
for li in layout.each_layer():
    layer_index, datatype = li.layer, li.datatype
    shapes = cell.shapes(li)
    
    # 4) Walk through each shape on that layer
    for i, shape in enumerate(shapes.each()):
        if shape.is_polygon():
            poly = shape.polygon         # a pya.Polygon object
            pts = [(pt.x, pt.y) for pt in poly.each_point()]
            print(f"Layer {layer_index}, Datatype {datatype}, Polygon #{i}:")
            print(f"  {len(pts)} points -> {pts}")
