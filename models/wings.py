"""
This module contains various classes that are based on airfoil shapes.

Classes:
    Wing: base class of all classes implemented in the module
    HorizontalTail: 
    VerticalTail: 
"""

"""Extra classes for wing objects and propeller objects that are based on various Airfoil sections. A horizontal tail is a type of wing, a vertical tail is a single sided wing, and a propeller is a wing with a twist that is rotated about an axis."""

from .airfoils import Airfoil

class Section(Airfoil):
    def __init__(self, root_foil, tip_foil, root_chord, tip_chord, span, twist, dihedral):
        pass
    def add_control_surface(self, root_position, tip_position, chord_percent):
        pass

class Wing():
    def _init__(self):
        self.sections = []

    def add_section(self, spanwise_position, chord, sweep, twist, dihedral, airfoilname, airfoil):
        # Construct a section object, add airfoil to wing.sections
        # only one of airfoilname or airfoil may be used
        # behaviour of root airfoil
        # behaviour of tip airfoil
        pass
    def add_control_surface(self, root_position, tip_position, chord_percent):
        pass

class HorizontalTail(Wing):
    def __init__(self):
        pass

class VerticalTail(Wing):
    def __init__(self):
        pass

class Propeller(Wing):
    def __init__(self, span, pitch):
        pass