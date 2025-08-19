import klayout.db as pya

# 1) Read the GDS
layout = pya.Layout()
layout.read("pcsource.gds")

# 2) Grab the top cell
cell = layout.top_cell()

# 3) Get layer handles and infos
layer_idxs  = layout.layer_indexes()   # integer layer handles
layer_infos = layout.layer_infos()     # corresponding pya.LayerInfo

# 4) Iterate all shapes, handling boxes, polygons, paths, text, pins
for idx, info in zip(layer_idxs, layer_infos):
    layer_no, datatype = info.layer, info.datatype
    shapes = cell.shapes(idx)
    for i, shape in enumerate(shapes.each()):
        if shape.is_box():
            # axis-aligned rectangle
            box = shape.box
            x1, y1 = box.p1.x, box.p1.y
            x2, y2 = box.p2.x, box.p2.y
            pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
            print(f"Layer {layer_no}, DType {datatype}, Box #{i}:")
            print(f"  4 points → {pts}")
        elif shape.is_polygon():
            # arbitrary polygon
            poly = shape.polygon
            pts = [(pt.x, pt.y) for pt in poly.each_point()]
            print(f"Layer {layer_no}, DType {datatype}, Polygon #{i}:")
            print(f"  {len(pts)} points → {pts}")
        elif shape.is_path():
            # path
            path = shape.path
            pts = [(pt.x, pt.y) for pt in path.each_point()]
            width = path.width
            print(f"Layer {layer_no}, DType {datatype}, Path #{i}:")
            print(f"  Width = {width}, Points → {pts}")
        elif shape.is_text():
            # text
            text = shape.text
            print(f"Layer {layer_no}, DType {datatype}, Text #{i}:")
            print(f"  Text = '{text.string}', at ({text.trans.disp.x}, {text.trans.disp.y})")
        else:
            # other shapes (paths, texts…) if you care
            print(f"Layer {layer_no}, DType {datatype}, Shape #{i}: Unhandled type {shape.shape_type}")

