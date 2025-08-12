# KLayout PCell: PMOSSwitchArray
# -------------------------------------------------------------
# Template PCell for an array of switchable PMOS transistors,
# placed side-by-side. Bottom diffusion (drain) gets contacts
# up to Metal1; the top diffusion is left clean for abutment so
# that sources short together by abutment when tiling vertically.
#
# This is a *template* for the IHP SG13G2 process. You MUST map
# the LayerInfo values below to your PDK's layers (OD, PO, PIMP,
# NWELL, CO, M1, N-tap, etc.) and set design-rule numbers from
# the PDK. The geometry math aims to be clean/DRC-friendly but
# it's not a substitute for your PDK deck.
#
# Usage (in KLayout):
# - Save inside a .py macro and register as a library, or paste
#   into the Macro Development IDE and run.
# - Instantiate via: Draw > PCell > Library > PMOSSwitchArray
# - Abut two instances vertically to short the top diffusion.
#
# Parameters:
#   n                 : number of devices in the horizontal array
#   w                 : gate width (um)
#   l                 : gate length (um)
#   sd_ext            : S/D diffusion extension beyond poly (um)
#   bot_gap           : diffusion break (OD gap) at bottom edge (um)
#   cont_size         : contact cut size (um)
#   cont_pitch        : contact pitch (um)
#   cont_enc_od       : OD enclosure of contact (um)
#   cont_enc_m1       : M1 enclosure of contact (um)
#   po_ovl_od         : poly overhang over OD (um)
#   po_space          : poly-to-poly min space (um)
#   m1_lbl_prefix     : text label prefix on each drain ("D")
#   add_gate_strap    : if True, adds a shared gate strap in M1 on left
#   add_nwell_tap     : if True, places an N-well tap tied to M1 at left
#
# Abutment strategy:
# - Top OD edge is left without contacts and has an OD keepout.
# - When you place a second copy above, OD will touch/merge and
#   form a continuous source diffusion.
# -------------------------------------------------------------

import pya

class PMOSSwitchArray(pya.PCellDeclarationHelper):
    def __init__(self):
        super(PMOSSwitchArray, self).__init__()

        # ---------- Parameters ----------
        self.param("n", self.TypeInt, "Number of devices", default=4)
        self.param("w", self.TypeDouble, "Gate width (um)", default=1.0)
        self.param("l", self.TypeDouble, "Gate length (um)", default=0.13)
        self.param("sd_ext", self.TypeDouble, "S/D OD extension (um)", default=0.10)
        self.param("bot_gap", self.TypeDouble, "Bottom OD gap for drain isolation (um)", default=0.20)

        self.param("cont_size", self.TypeDouble, "Contact size (um)", default=0.14)
        self.param("cont_pitch", self.TypeDouble, "Contact pitch (um)", default=0.24)
        self.param("cont_enc_od", self.TypeDouble, "OD enclosure of contact (um)", default=0.03)
        self.param("cont_enc_m1", self.TypeDouble, "M1 enclosure of contact (um)", default=0.03)

        self.param("po_ovl_od", self.TypeDouble, "Poly over OD (um)", default=0.05)
        self.param("po_space", self.TypeDouble, "Poly to poly spacing (um)", default=0.28)

        self.param("m1_lbl_prefix", self.TypeString, "M1 drain label prefix", default="D")
        self.param("add_gate_strap", self.TypeBoolean, "Add shared gate strap (M1)", default=True)
        self.param("add_nwell_tap", self.TypeBoolean, "Add N-well tap at left", default=True)

        # ---------- Layers (map to your SG13G2 PDK) ----------
        # Replace LayerInfo(GDS_LAYER, GDS_DATATYPE) with PDK values.
        self.param("ly_od", self.TypeLayer, "Diffusion (OD)", default=pya.LayerInfo(65, 20))
        self.param("ly_pimp", self.TypeLayer, "P+ implant", default=pya.LayerInfo(70, 44))
        self.param("ly_nwell", self.TypeLayer, "N-Well", default=pya.LayerInfo(64, 44))
        self.param("ly_po", self.TypeLayer, "Poly (Gate)", default=pya.LayerInfo(66, 20))
        self.param("ly_co", self.TypeLayer, "Contact (CO)", default=pya.LayerInfo(67, 44))
        self.param("ly_m1", self.TypeLayer, "Metal1 (M1)", default=pya.LayerInfo(68, 44))
        self.param("ly_lbl", self.TypeLayer, "Text Labels", default=pya.LayerInfo(68, 5))

        # N-well tap uses N+ active inside N-well; some PDKs have a dedicated layer.
        self.param("ly_ntap", self.TypeLayer, "N-well tap diffusion (if separate)", default=pya.LayerInfo(65, 21))

        # Draw boundary/PR boundary (optional)
        self.param("ly_pr", self.TypeLayer, "Placement boundary", default=pya.LayerInfo(235, 0))

    def display_text_impl(self):
        return f"PMOSSwitchArray_n{self.n}_W{self.w}_L{self.l}"

    def co_bbox(self, x_center, y_center, size):
        s = size/2.0
        return pya.Box.from_dpoint(pya.DPoint(x_center - s, y_center - s), pya.DPoint(x_center + s, y_center + s))

    def place_contact_row(self, shapes, co_ly, start_x, y_center, n_cuts, size, pitch):
        x = start_x
        for _ in range(n_cuts):
            shapes(co_ly).insert(self.co_bbox(x, y_center, size))
            x += pitch

    def produce_impl(self):
        dbu = self.layout.dbu
        to_dbu = lambda x: int(round(x / dbu))

        # Layers
        ly_od = self.layout.layer(self.ly_od)
        ly_pimp = self.layout.layer(self.ly_pimp)
        ly_nwell = self.layout.layer(self.ly_nwell)
        ly_po = self.layout.layer(self.ly_po)
        ly_co = self.layout.layer(self.ly_co)
        ly_m1 = self.layout.layer(self.ly_m1)
        ly_lbl = self.layout.layer(self.ly_lbl)
        ly_ntap = self.layout.layer(self.ly_ntap)
        ly_pr = self.layout.layer(self.ly_pr)

        shapes = self.cell.shapes

        # Derived dimensions
        gate_pitch = self.l + 2*self.sd_ext + self.po_space
        array_width = self.n * gate_pitch - self.po_space  # last finger has no trailing space

        # Vertical stack: define y=0 at bottom drain contact centerline
        # OD rectangle height to accommodate contacts at bottom and abut at top
        od_height = self.w + 2*self.sd_ext + self.bot_gap

        # Coordinates
        bottom_y = 0.0
        drain_co_y = bottom_y + self.cont_enc_od + self.cont_size/2.0
        od_bottom = bottom_y
        od_top = od_bottom + od_height
        gate_y0 = od_bottom + self.sd_ext
        gate_y1 = gate_y0 + self.w

        # Draw single continuous OD stripe per device, separated by OD breaks at the bottom only.
        # For simplicity: one large OD for the whole row, then carve a bottom notch between devices.
        od_box = pya.DBox(0.0, od_bottom, array_width, od_top)
        shapes(ly_od).insert(pya.Box.from_dbox(od_box))
        # P+ implant follows OD
        shapes(ly_pimp).insert(pya.Box.from_dbox(od_box))

        # Gates and OD bottom notches (to isolate drains between devices)
        x0 = 0.0
        for i in range(self.n):
            # Gate rectangle
            g_x0 = x0 + self.sd_ext
            g_x1 = g_x0 + self.l
            g_box = pya.DBox(g_x0, gate_y0 - self.po_ovl_od, g_x1, gate_y1 + self.po_ovl_od)
            shapes(ly_po).insert(pya.Box.from_dbox(g_box))

            # Bottom OD notch centered between fingers to prevent source/drain merge at bottom
            if i < self.n - 1:
                notch_x0 = x0 + gate_pitch - self.po_space/2.0
                notch_x1 = notch_x0 + self.po_space
                notch_box = pya.DBox(notch_x0, od_bottom, notch_x1, od_bottom + self.bot_gap)
                # Subtract notch from OD and PIMP via boolean (erase)
                # KLayout PCells cannot directly boolean on the fly per shape list; use Region
                od_reg = pya.Region(self.cell.begin_shapes_rec(ly_od))
                pim_reg = pya.Region(self.cell.begin_shapes_rec(ly_pimp))
                notch = pya.Region(pya.Box.from_dbox(notch_box))
                od_reg -= notch
                pim_reg -= notch
                shapes(ly_od).clear()
                shapes(ly_pimp).clear()
                shapes(ly_od).insert(od_reg)
                shapes(ly_pimp).insert(pim_reg)

            x0 += gate_pitch

        # Bottom drain contacts to M1: place a contact bar per device at bottom inside OD
        x0 = 0.0
        for i in range(self.n):
            # Drain contact window spans the OD width under the gate (plus margins)
            od_left = x0
            od_right = x0 + (self.l + 2*self.sd_ext)

            # Fit as many contacts as possible across [od_left+enc, od_right-enc]
            usable_w = (od_right - od_left) - 2*self.cont_enc_od
            n_cuts = max(1, int((usable_w + (self.cont_pitch - self.cont_size)) // self.cont_pitch))
            # Center the array
            total_cuts_w = n_cuts * self.cont_pitch - (self.cont_pitch - self.cont_size)
            start_x = od_left + self.cont_enc_od + 0.5*(usable_w - total_cuts_w) + self.cont_size/2.0

            # Contacts
            self.place_contact_row(shapes, ly_co, start_x, drain_co_y, n_cuts, self.cont_size, self.cont_pitch)

            # M1 landing (simple rectangle encompassing contacts)
            m1_y0 = drain_co_y - (self.cont_size/2.0 + self.cont_enc_m1)
            m1_y1 = drain_co_y + (self.cont_size/2.0 + self.cont_enc_m1)
            m1_x0 = start_x - self.cont_size/2.0 - self.cont_enc_m1
            m1_x1 = start_x + (n_cuts - 1)*self.cont_pitch + self.cont_size/2.0 + self.cont_enc_m1
            shapes(ly_m1).insert(pya.Box.from_dbox(pya.DBox(m1_x0, m1_y0, m1_x1, m1_y1)))

            # Label each drain
            shapes(ly_lbl).insert(pya.Text(f"{self.m1_lbl_prefix}{i}", pya.DTrans(pya.DTrans.R0, (m1_x0 + m1_x1)/2.0, m1_y1 + 0.05)))

            x0 += gate_pitch

        # Optional shared gate strap in M1 on the left
        if self.add_gate_strap:
            gstrap_x = - (self.po_space)  # to the left of first gate
            # Vertical M1 bar spanning all gates
            shapes(ly_m1).insert(pya.Box.from_dbox(pya.DBox(gstrap_x - 0.1, gate_y0 - 0.1, gstrap_x + 0.1, gate_y1 + 0.1)))
            # Poly-to-M1 connection using contacts (replace with PO-VIA layer if your PDK has it)
            # Here we simply drop a short poly extension and a few contacts as a placeholder
            po_stub = pya.DBox(gstrap_x, gate_y0 - self.po_ovl_od, self.sd_ext/2.0, gate_y1 + self.po_ovl_od)
            shapes(ly_po).insert(pya.Box.from_dbox(po_stub))
            # Contact ladder between PO and M1 is PDK-specific; keepout for now

        # Optional N-well and well tap at left
        nwell_bbox = pya.DBox(-0.5, od_bottom - 0.5, array_width + 0.5, od_top + 0.5)
        shapes(ly_nwell).insert(pya.Box.from_dbox(nwell_bbox))
        if self.add_nwell_tap:
            tap_w = 0.6
            tap_h = 0.6
            tap_box = pya.DBox(-0.9, gate_y0, -0.9 + tap_w, gate_y0 + tap_h)
            shapes(ly_ntap).insert(pya.Box.from_dbox(tap_box))
            # COs inside tap
            # Simple 2x2 contacts
            tx0 = tap_box.left + self.cont_enc_od + self.cont_size/2.0
            ty0 = tap_box.bottom + self.cont_enc_od + self.cont_size/2.0
            for ix in range(2):
                for iy in range(2):
                    cx = tx0 + ix*self.cont_pitch
                    cy = ty0 + iy*self.cont_pitch
                    shapes(ly_co).insert(self.co_bbox(cx, cy, self.cont_size))
            # M1 over tap
            shapes(ly_m1).insert(pya.Box.from_dbox(tap_box.enlarged(self.cont_enc_m1)))

        # Top OD left for abutment: add a small OD keepout label/marker (optional)
        shapes(ly_lbl).insert(pya.Text("ABUT_TOP_OD", pya.DTrans(pya.DTrans.R0, array_width/2.0, od_top + 0.1)))

        # Placement boundary
        pr = pya.DBox(-1.2, od_bottom - 0.8, array_width + 0.8, od_top + 0.8)
        shapes(ly_pr).insert(pya.Box.from_dbox(pr))

# Register as a library so it appears in the PCell list
class PMOSSwitchArrayLib(pya.Library):
    def __init__(self):
        super(PMOSSwitchArrayLib, self).__init__()
        self.description = "Templates for IHP SG13G2 (user-mapped layers)"
        self.layout().register_pcell("PMOSSwitchArray", PMOSSwitchArray())
        self.register("PMOSSwitchArrayLib")

# Instantiate library on load
def load_libraries():
    PMOSSwitchArrayLib()

load_libraries()
