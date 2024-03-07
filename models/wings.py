"""Extra classes for wing objects and propeller objects that arebased on various Airfoil sections."""
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