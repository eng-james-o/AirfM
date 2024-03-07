"""
Helper functions
"""
import os

def get_foils(data_path = r"C:/Users/PC/Documents/qt_projects/AirfoilManipulate/data/coord_seligFmt/"):
    files = [f for f in os.listdir(data_path)]# if os.path.isfile(f)]
    return files

if __name__ == "__main__":
    airfoils = get_foils()
    #print(airfoils)