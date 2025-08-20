# -*- coding: utf-8 -*-
import pya

# FEOL contact row (minimal PCell example)

class feol_contact(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        # Parameters
        self.param("l", self.TypeInt, "contact length (nm)", default=260)
        self.param("h", self.TypeInt, "contact height (nm)", default=160)
        self.param("ly_active", self.TypeLayer, "active area (diffusion)", default=pya.LayerInfo(1, 0))
        self.param("ly_po",     self.TypeLayer, "Poly (Gate)",             default=pya.LayerInfo(5, 0))
        self.param("ly_co",     self.TypeLayer, "Contact (CO)",            default=pya.LayerInfo(6, 0))
        self.param("ly_m1",     self.TypeLayer, "Metal1 (M1)",             default=pya.LayerInfo(8, 0))
        self.param("ly_pimp",   self.TypeLayer, "P+ implant",              default=pya.LayerInfo(14, 0))
        self.param("ly_nwell",  self.TypeLayer, "N-Well",                  default=pya.LayerInfo(31, 0))
        self.param("ly_pr",     self.TypeLayer, "Placement boundary",      default=pya.LayerInfo(63, 0))

    def display_text_impl(self):
        return f"feol_contact_l{self.l}_h{self.h}"

    def coerce_parameters_impl(self):
        # Keep parameters valid; add rules as needed
        if self.l <= 260: self.l = 260
        if self.h <= 160: self.h = 160

    def produce_impl(self):
        # Resolve layers
        ly_active = self.layout.layer(self.ly_active)
        ly_po     = self.layout.layer(self.ly_po)
        ly_co     = self.layout.layer(self.ly_co)
        ly_m1     = self.layout.layer(self.ly_m1)
        ly_pimp   = self.layout.layer(self.ly_pimp)
        ly_nwell  = self.layout.layer(self.ly_nwell)
        ly_pr     = self.layout.layer(self.ly_pr)

        contact_size    = 160
        contact_distance= 180
        contact_pitch   = contact_size + contact_distance
        metal1extension =   0   # metal 1 extension
        metal1endcap    =  50   # metal 1 end cap
        l = self.l
        h = self.h
        x0 = 0
        y0 = 0
        n_cuts_x    = max(0, (l + contact_distance - 2 * metal1endcap) // contact_pitch)
        n_cuts_y    = max(0, (h + contact_distance - 2 * metal1extension) // contact_pitch)
        xext = n_cuts_x * contact_pitch - contact_distance
        yext = n_cuts_y * contact_pitch - contact_distance
        start_x = (l - xext) // 2
        start_y = (h - yext) // 2

        shapes = self.cell.shapes
        # place CO cuts
        for y in range(n_cuts_y):
            for x in range(n_cuts_x):
                xl = start_x + x * contact_pitch
                xr = xl + contact_size
                yb = start_y + y * contact_pitch
                yt = yb + contact_size
                shapes(ly_co).insert(pya.Box(xl, yb, xr, yt))
        # M1 landing bar that covers the row of contacts
        shapes(ly_m1).insert(pya.Box(x0, y0, x0 + l, y0 + h))

# Register library
class BasicsLib(pya.Library):
    def __init__(self):
        super().__init__()  # important
        self.description = "A very basic pcell library"
        # Register PCells
        self.layout().register_pcell("FEOL contacts", feol_contact())
        # Register the library by name
        self.register("BasicsLib")

def load_libraries():
    BasicsLib()

load_libraries()

