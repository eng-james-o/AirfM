"""Extra classes for wing objects and propeller objects that are based on various Airfoil sections. A horizontal tail is a type of wing, a vertical tail is a single sided wing, and a propeller is a wing with a twist that is rotated about an axis."""
print("wings imported")

class wing:
    def _init__(self):
        self.sections = []

    def add_foil(self, spanwise_position, chord, sweep, twist, dihedral, airfoilname, airfoil):
        # Construct an airfoil object, add airfoil to wing.sections
        # only one of airfoilname or airfoil may be used
        # behaviour of root airfoil
        # behaviour of tip airfoil
        pass
    def add_control_surface(self, root_position, tip_position, chord_percent):
        pass

class propeller(wing):
    def __init__(self, span, pitch):
        pass