# -*- coding: utf-8 -*-
import pya

# Switched PMOS cascode (minimal PCell example)

class SwitchedPMOSCascode(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        # Parameters
        self.param("l", self.TypeInt, "cascode length (nm)", default=400)
        self.param("w", self.TypeInt, "cascode width (nm)",  default=300)
        self.param("ly_active", self.TypeLayer, "active area (diffusion)", default=pya.LayerInfo(1, 0))
        self.param("ly_po",     self.TypeLayer, "Poly (Gate)",             default=pya.LayerInfo(5, 0))
        self.param("ly_co",     self.TypeLayer, "Contact (CO)",            default=pya.LayerInfo(6, 0))
        self.param("ly_m1",     self.TypeLayer, "Metal1 (M1)",             default=pya.LayerInfo(8, 0))
        self.param("ly_pimp",   self.TypeLayer, "P+ implant",              default=pya.LayerInfo(14, 0))
        self.param("ly_nwell",  self.TypeLayer, "N-Well",                  default=pya.LayerInfo(31, 0))
        self.param("ly_pr",     self.TypeLayer, "Placement boundary",      default=pya.LayerInfo(63, 0))

    def display_text_impl(self):
        return f"Switched PMOS cascode_W{self.w}_L{self.l}"

    def coerce_parameters_impl(self):
        # Keep parameters valid; add rules as needed
        if self.l <= 130: self.l = 130
        if self.w <= 130: self.w = 130

    def produce_impl(self):
        # Resolve layers
        ly_active = self.layout.layer(self.ly_active)
        ly_po     = self.layout.layer(self.ly_po)
        ly_co     = self.layout.layer(self.ly_co)
        ly_m1     = self.layout.layer(self.ly_m1)
        ly_pimp   = self.layout.layer(self.ly_pimp)
        ly_nwell  = self.layout.layer(self.ly_nwell)
        ly_pr     = self.layout.layer(self.ly_pr)

        shapes = self.cell.shapes
        lhalf=self.l//2
        w=self.w
        whalf=w//2
        # Draw some simple geometry (database units)
        shapes(ly_active).insert(pya.Box(290, -(lhalf+230), 290+w, (lhalf+340)))
        shapes(ly_po).insert(    pya.Box(-150, -lhalf, 470+w, lhalf))
        shapes(ly_co).insert(    pya.Box(-80,  -80,   80,  80))
        shapes(ly_co).insert(    pya.Box(whalf+210, lhalf+110, whalf+370, lhalf+270))
        shapes(ly_m1).insert(    pya.Box(-80, -130,   80, 130))
        shapes(ly_m1).insert(    pya.Box(whalf+160, lhalf+110, whalf+420, lhalf+270))
        shapes(ly_pimp).insert(  pya.Box(-10, -(lhalf+410),  590+w, (lhalf+520)))
        shapes(ly_nwell).insert( pya.Box(-30, -(lhalf+640),  610+w, (lhalf+650)))
        shapes(ly_pr).insert(    pya.Box(-190, -(lhalf+640),  610+w, (lhalf+650)))

class PMOSSourcesLib(pya.Library):
    def __init__(self):
        super().__init__()  # important
        self.description = "Switched PMOS bit"
        # Register PCells
        self.layout().register_pcell("SwitchedPMOSCascode", SwitchedPMOSCascode())
        # Register the library by name
        self.register("PMOSSourcesLib")

# Instantiate library on load
PMOSSourcesLib()

