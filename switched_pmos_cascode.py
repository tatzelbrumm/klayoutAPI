# -*- coding: utf-8 -*-
import pya

# Switched PMOS cascode (minimal PCell example)

class SwitchedPMOSCascode(pya.PCellDeclarationHelper):
    def __init__(self):
        super().__init__()
        # Parameters
        self.param("l", self.TypeDouble, "cascode length", default=0.4)
        self.param("w", self.TypeDouble, "cascode width",  default=0.3)
        self.param("ly_active", self.TypeLayer, "active area (diffusion)", default=pya.LayerInfo(1, 0))
        self.param("ly_po",     self.TypeLayer, "Poly (Gate)",             default=pya.LayerInfo(5, 0))
        self.param("ly_co",     self.TypeLayer, "Contact (CO)",            default=pya.LayerInfo(6, 0))
        self.param("ly_m1",     self.TypeLayer, "Metal1 (M1)",             default=pya.LayerInfo(8, 0))
        self.param("ly_pimp",   self.TypeLayer, "P+ implant",              default=pya.LayerInfo(14, 0))
        self.param("ly_nwell",  self.TypeLayer, "N-Well",                  default=pya.LayerInfo(31, 0))

    def display_text_impl(self):
        return f"Switched PMOS cascode_W{self.w}_L{self.l}"

    def coerce_parameters_impl(self):
        # Keep parameters valid; add rules as needed
        if self.l <= 0: self.l = 0.1
        if self.w <= 0: self.w = 0.1

    def produce_impl(self):
        # Resolve layers
        ly_active = self.layout.layer(self.ly_active)
        ly_po     = self.layout.layer(self.ly_po)
        ly_co     = self.layout.layer(self.ly_co)
        ly_m1     = self.layout.layer(self.ly_m1)
        ly_pimp   = self.layout.layer(self.ly_pimp)
        ly_nwell  = self.layout.layer(self.ly_nwell)

        shapes = self.cell.shapes
        # Draw some simple geometry (database units)
        shapes(ly_active).insert(pya.Box(290, -380, 440, 380))
        shapes(ly_po).insert(    pya.Box(-150, -150, 620, 150))
        shapes(ly_co).insert(    pya.Box(-80,  -80,   80,  80))
        shapes(ly_m1).insert(    pya.Box(-80, -130,   80, 130))
        shapes(ly_pimp).insert(  pya.Box(-10, -560,  740, 560))
        shapes(ly_nwell).insert( pya.Box(-30, -790,  760, 790))

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

