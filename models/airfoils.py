"""
This module contains various airfoil classes and other classes that are based on airfoil shapes.

Classes:
    Airfoil: base class of all classes implemented in the module
    NACA4DigitFoil:
    NACA5DigitFoil:
"""
# This Python file uses the following encoding: utf-8

# from typing import Dict
import numpy as np
from scipy.interpolate import interp1d
# from scipy.misc import derivative
import matplotlib.pyplot as plt
import re

import os
# from pathlib import Path
# import sys

from PySide2.QtCore import Property, QAbstractListModel, QObject, Qt, Signal, Slot
from logger_config import logger

## remember to update the _data attribute in the emethods that modify the airfoil data, such as initialise_foil(). since the _data attribute is what is being exposed to QML and not the 4 data arrays 

class Airfoil_new(QObject):
    """
    Creates an airfoil object which can be rotated, moved, scaled. Base class for all airfoil types defined in the module

    More detailed description, purpose, usage, important details

    Attributes:
        QUARTER_CHORD (tuple (float, float)): description
        PATH (str): description
        NAME (str): description
        NUM_POINTS (int): description
        UPPER (np.ndarray): description
        LOWER (np.ndarray): description
        UPPER_X (np.ndarray): description
        UPPER_Y (np.ndarray): description
        LOWER_X (np.ndarray): description
        LOWER_Y (np.ndarray): description
        PLANE (str): description
        INCIDENCE (float): description
        X (np.ndarray): description
        Y (np.ndarray): description
        Z (np.ndarray): description
    
    Methods:
        calculate_quarter_chord(): Calcualtes the position of the quarter chord of the airfoil
        calculate_chord(): Calculates the length of the chord of the airfoil
        count_points(): count the number of points for the upper curve and lower curves
        center_foil(): centers the coordinates of the foil to make the quarter chord lie at (0,0)
        order_points(): Order the airfoil coordinates such that the data goes from LE over the upper surface to TE and then back to LE over the lower surface
        load(): Load the data from the dat file into the object and returns 2 matrices upper and lower, which contain 2 vectors each: X and Y
        scale_to(): Scales the airfoil to the given chord
        translate_to(): Translates the airfoil to a desired x, y position
        rotate_to(): Rotates the airfoil to a specific angle
        normalise(): Normalise the airfoil to a unit chord
        plane(): Specify and change the plane to be used when exporting to solidworks txt, which requires 3 columns of airfoil data depending on the plane in which the foil will be used
        flip(): Flip the airfoil vertically or horizontally
        close_TE(): CLoses the trailing edge. if the trailing edge is closed, it does nothing. If blend_TE is set to True, this will close the TE to a point, or otherwise make the TE a short vertical line
        show(): Plots an airfoil using the airfoil data points
        export_curve_to(): Exports the airfoil coordinates to a file that is readable by CAD software
    """
    dataChanged = Signal()

    def __init__(self, airfoil_path=None, airfoil_name:str=None, plane:str="XY", incidence:float=None, chord:float=None, position:tuple=None, TE_treatment:str="point", parent=None):
        """
        Args:
            airfoil_path (str): path to airfoil dat file
            airfoil_data (list or np.ndarray): an iterable containing the vectors upper and lower of the coordinates of the airfoil. Only one of airfoil_path or airfoil_data can be used
            airfoil_name (str): the name of the foil. only used if airfoil_data is used and not airfoil_path
            plane (str): one of "XY", "YX", OR "YZ", "ZY" OR "XZ", "ZX". plane is defined horizontal first, then vertical. i.e XY has chord on X and thickness on Y. defaults to "XY"
            incidence (float): angle of incidence between chord and horizontal
            chord (float): chord value to scale the airfoil coordinates
            offset (float): the position offset of the airfoil (horizaontal, vertical)
            TE_treatment (str): how to treat the trailing edge. "point" closes the TE to a point, "line" closes the TE to a line
        """
        self.NAME = None
        super().__init__(parent)
        self.LOADED = False 
        # becomes true if data is in the airfoil
        # and false if it is empty, either upon initialisatoin, or reset

        if airfoil_path:
            # if path to airfoil data is given
            self.PATH = airfoil_path # save the path
            self.load(self.PATH) # load the airfoil data
            
            if not self.NAME and not airfoil_name:
                # no name has been supplied
                logger.error("No name has been supplied")
    
    @Slot(str)
    def load(self, filename:str, plane=None, incidence=None, chord=None, position=None, TE_treatment=None):
        """
    Reads a Selig-format airfoil file and returns the airfoil name,
    the total number of points, and four NumPy arrays:
    x_upper, y_upper, x_lower, y_lower.

    The file is expected to contain either a header (the first non-empty line)
    with the airfoil name or no header. In the latter case, the file's name
    (without extension) is used as the airfoil name.

    The coordinate data lines should have the format:
        [index]  x-coordinate  y-coordinate
    where the index is optional. In a Selig file the coordinates are usually
    ordered such that the first section (upper surface) runs from the trailing
    edge to the leading edge and the second section (lower surface) runs from
    the leading edge to the trailing edge. This function splits the data at the
    leading edge (identified as the point with the minimum x value) and then
    reverses each section so that:
      - x_upper, y_upper run from the leading edge to the trailing edge.
      - x_lower, y_lower run from the trailing edge to the leading edge.
    
    It also checks for a duplicate trailing edge point (often present in Selig files)
    and removes it before concatenation.
    
    Args:
        filename (str): Path to the airfoil file.
    
    Returns:
        name (str): Airfoil name.
        num_points (int): Total number of coordinate points defined in the file.
        x_upper (np.ndarray): x-coordinates for the upper surface.
        y_upper (np.ndarray): y-coordinates for the upper surface.
        x_lower (np.ndarray): x-coordinates for the lower surface.
        y_lower (np.ndarray): y-coordinates for the lower surface.
    """
        # Read and strip file lines; ignore completely blank lines.
        if filename == "":
            return

        with open(filename, 'r') as f:
            lines = f.readlines()
        lines = [line.strip() for line in lines if line.strip() != '']

        # Define a regex pattern to extract (optional index) and two numbers (x and y)
        # Pattern explanation:
        #   ^\s*           -> start of the line (allowing whitespace)
        #   (?:\d+\s+)?    -> an optional index followed by whitespace
        #   ([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)  -> x-coordinate (float, with optional exponent)
        #   \s+            -> whitespace separator
        #   ([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)  -> y-coordinate (float, with optional exponent)
        coordinate_pattern = re.compile(
            r'^\s*(?:\d+\s+)?([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)'
        )

        # Determine if the first non-empty line is a header (name) or coordinate data.
        if not lines:
            raise ValueError("File is empty.")
        first_line = lines[0]
        if coordinate_pattern.match(first_line):
            # No header present; use the file name (without extension) as the airfoil name.
            name = os.path.splitext(os.path.basename(filename))[0]
            data_lines = lines
        else:
            name = first_line
            data_lines = lines[1:]
        
        # Extract coordinate data using regex
        data = []
        for line in data_lines:
            match = coordinate_pattern.match(line)
            if match:
                try:
                    x_val = float(match.group(1))
                    y_val = float(match.group(2))
                    data.append((x_val, y_val))
                except ValueError:
                    continue  # Skip lines that cannot be parsed as floats
        
        num_points = len(data)
        if num_points < 2:
            raise ValueError("Not enough data points were found in the file.")
        
        # Convert to NumPy array for easier processing
        data = np.array(data)  # shape (num_points, 2)
        x_all = data[:, 0]
        y_all = data[:, 1]
        
        # Identify the leading edge point as the one with the minimum x value
        i_le = np.argmin(x_all)
        
        # According to Selig format:
        # - Upper surface data: from the start of the file (trailing edge) to the leading edge.
        # - Lower surface data: from the leading edge to the end of the file (trailing edge).
        upper_data = data[:i_le+1]
        lower_data = data[i_le:]
        
        # Remove a duplicate trailing edge point if it exists.
        # Typically the trailing edge appears as the first point of the upper surface and the last point of the lower surface.
        if np.allclose(upper_data[0], lower_data[-1], atol=1e-6):
            lower_data = lower_data[:-1]
        
        # Reorder the data to match the desired output:
        # For the upper surface: desired order is from leading edge to trailing edge.
        #   (File order is trailing edge -> ... -> leading edge, so we reverse it)
        upper_data_reversed = upper_data[::-1]
        
        # For the lower surface: desired order is from trailing edge to leading edge.
        #   (File order is leading edge -> ... -> trailing edge, so we reverse it)
        lower_data_reversed = lower_data[::-1]
        
        # Split into separate arrays.
        x_upper = upper_data_reversed[:, 0]
        y_upper = upper_data_reversed[:, 1]
        x_lower = lower_data_reversed[:, 0]
        y_lower = lower_data_reversed[:, 1]

        # Add data into the class instance parameters
        self.NAME = name
        self.NUM_POINTS = num_points
        # self.dataChanged.emit() # this should already be emited by the self._data property definition
        
        x = np.hstack((x_lower, x_upper[::-1]))
        y = np.hstack((y_lower, y_upper[::-1]))
        self._data = np.vstack((x, y)).T

        if plane or incidence or chord or position or TE_treatment:
            self.initialise_foil(plane=plane, incidence=incidence, chord=chord, position=position, TE_treatment=TE_treatment)

        # return name, num_points, x_upper, y_upper, x_lower, y_lower
    
    def initialise_foil(self, plane, incidence, chord, position, TE_treatment):
        # self.close_TE(blend = blend_trailing_edge)

        self.PLANE = plane
        self.INCIDENCE = 0
        
        # center foil, then scale, then rotate, then translate
        # center the airfoil quarter_chord
        # move this functionality to a separate function thqt is called here, and is also called if the airfoil is initialised empty and loaded later
        
        # if self.LOADED:
        self.center_foil()

            # but if chord is given scale the foil to the given chord. 
        if chord:
            self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y = self.scale_to(chord)

            # rotate airfoil
        if incidence:
            self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y = self.rotate_to(incidence)

            # translate foil to desired position
        if position:
            self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y = self.translate_to(*position)
            
        # self.X, self.Y = self.order_points()
        # self.Z = np.zeros_like(self.X)

    def calculate_quarter_chord(self):
        """
        Calcualtes the position of the quarter chord of the airfoil and sets the self.QUARTER_CHORD parameter

        Returns:
            tuple: x, y
        """
        # self.QUARTER_CHORD =  (((self.UPPER_X[-1] - self.UPPER_X[0])/4)+self.UPPER_X[0], ((self.UPPER_Y[-1] - self.UPPER_Y[0])/4)+self.UPPER_Y[0])
        return (((self.UPPER_X[-1] - self.UPPER_X[0])/4)+self.UPPER_X[0], ((self.UPPER_Y[-1] - self.UPPER_Y[0])/4)+self.UPPER_Y[0])
    
    def calculate_chord(self):
        """
        Calculates the length of the chord of the airfoil

        Returns:
            float: chord
        """
        return np.sqrt((self.UPPER_X[-1] - self.UPPER_X[0])**2 + (self.UPPER_Y[-1] - self.UPPER_Y[0])**2)
    
    def count_points(self):
        """
        count the number of points for the upper curve and lower curves. This method is necessary if the airfoil_data is given instead of the path
        
        Args:
        Returns:
            tuple: num_upper, num_lower
        """
        pass

    def center_foil(self):
        '''centers the coordinates of the foil to make the quarter chord lie at (0,0)'''
        
        self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y = self.translate_to(0,0)

    def order_points(self):
        """
        Order the airfoil coordinates such that the data goes from LE over the upper surface to TE and then back to LE over the lower surface.

        Returns: 
            tuple: X, Y - X coordinates and Y coordinates of the foil from LE to TE and back to LE
        """
        # check if the data is in the correct order.
        # CORRECT ORDER: x values of upper curve goes from small to high and lower curve from high to small
        if (self.UPPER_X[0] < self.UPPER_X[-1]) and (self.LOWER_X[0] < self.LOWER_X[-1]):
            # Upper curve goes from small to high but lower cuve also goes from low to high. lower curve needs to reverse
            self.LOWER_X = np.flipud(self.LOWER_X)
            self.LOWER_Y = np.flipud(self.LOWER_Y)
            print('Lower curve reversed')
        
        # implement code to remove duplicate TE point
        # if last point of upper curve == first point of lower curve, remove the TE point
        # first point in lower curve
        if (self.UPPER_X[-1] == self.LOWER_X[0]) and (self.UPPER_Y[-1] == self.LOWER_Y[0]):
            lower_x = self.LOWER_X[1:]
            lower_y = self.LOWER_Y[1:]
        else:
            lower_x = self.LOWER_X[:]
            lower_y = self.LOWER_Y[:]

        # concatenate X and Y coordinates
        X = np.concatenate((self.UPPER_X, lower_x))
        Y = np.concatenate((self.UPPER_Y, lower_y))

        return X, Y

    @Slot()    
    def getData(self):
        # fix this, since self._data does not exist yet
        return self._data
    
    data = Property(np.ndarray, fget=getData, notify=dataChanged)

    def scale_to(self, chord:float)->tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Scales the airfoil to the given chord and returns upper_x, upper_y, lower_x, lower_y to be assigned back into the Instance attributes
        Args:
            chord: the desired chord of the airfoil
        
        Returns:
            tuple: upper_x, upper_y, lower_x, lower_y
        """
        #calculate the scaling factor based on the current chord and the desired chord
        old_chord = self.calculate_chord()
        sc_factor = chord / old_chord
        
        # if quarter_chord is not at (0,0), you need to translate it to (0,0), perform scale operation and restore the translation
        quarter_chord = self.calculate_quarter_chord()
        if quarter_chord != (0.0, 0.0):
            x_u_t, y_u_t, x_l_t, y_l_t = self.__translate(self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y, -quarter_chord[0], -quarter_chord[1])
            x_u_s, y_u_s, x_l_s, y_l_s = self.__scale(x_u_t, y_u_t, x_l_t, y_l_t, sc_factor)
            x_u_o, y_u_o, x_l_o, y_l_o = self.__translate(x_u_s, y_u_s, x_l_s, y_l_s, quarter_chord[0], quarter_chord[1])
        else:
           x_u_o, y_u_o, x_l_o, y_l_o = self.__scale(self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y, sc_factor)

        return x_u_o, y_u_o, x_l_o, y_l_o

    def translate_to(self, x_position:float, y_position:float):
        """
        Translates the airfoil to a desired x, y position
        Args:
            x_position (float): desired x position of the foil
            y_position (float): desired y position of the foil

        Returns:
            Tuple (tuple): upper_x, upper_y, lower_x, lower_y
        """
        # calculate the distance between the quarter chord and the desired position
        quarter_chord_x, quarter_chord_y = self.calculate_quarter_chord()

        dx = x_position - quarter_chord_x
        dy = y_position - quarter_chord_y
        x_u_t, y_u_t, x_l_t, y_l_t = self.__translate(self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y, dx, dy)

        return x_u_t, y_u_t, x_l_t, y_l_t

    def rotate_to(self, angle):
        """
        Rotates the airfoil to a specific angle
        Args:
            angle
        
        Returns:
            tuple
        """
        da = angle - self.INCIDENCE

        x_u_r, y_u_r, x_l_r, y_l_r = self.__rotate(self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y, da)

        # update foil incidence angle
        self.INCIDENCE = angle

        return x_u_r, y_u_r, x_l_r, y_l_r
    
    def normalise(self):
        """
        Normalise the airfoil to a unit chord
        """
        # consider normalise after the foil has been offset, which will require a more robust implementation
        pass

    def plane(self, plane):
        """
        Specify and change the plane to be used when exporting to solidworks txt, which requires 3 columns
        of airfoil data depending on the plane in which the foil will be used
        """
        # if plane is xy or XY, X data maps to X column and Y data maps to Y column
        # if plane is yx or YX, X data maps to Y column and Y data maps to X column
        # if plane is xz or XZ, X data maps to X column and Y data maps to Z column
        # if plane is zx or ZX, X data maps to Z column and Y data maps to X column
        # if plane is yz or YZ, X data maps to Y column and Y data maps to Z column
        # if plane is zy or ZY, X data maps to Z column and Y data maps to Y column
        # merge the implementation of the plane and flip methods
        pass

    def flip(self, axis="hor"):
        """
        Flip the airfoil vertically or horizontally
        """
        pass

    def close_TE(self, blend):
        """
        CLoses the trailing edge. if the trailing edge is closed, it does nothing.
        If blend_TE is set to True, this will close the TE to a point, or otherwise make the TE a short vertical line
        Short TE line is preferable for hot-wire manufacturing but choice is left to user
        """
        ### does this implementation add a new point to the trailing edge or does it simply move the last point to the middle of the trailing edge?
        # also ensure that the line does not exceed a certain threshold size for very large scaled foils
        # call this function before any transformation
        # if x_upper[-1] == y_upper[-1]
        
        if (self.UPPER_X[-1] != self.LOWER_X[-1]):
            self.UPPER_X[-1] = self.LOWER_X[-1] = (self.UPPER_X[-1] + self.LOWER_X[-1])/2

        if self.UPPER_Y[-1] != self.LOWER_Y[-1]:
            if blend:
                self.UPPER_Y[-1] = self.LOWER_Y[-1] = (self.UPPER_Y[-1] + self.LOWER_Y[-1])/2
            else:
                # close TE as a line instead of to a point. simply add a point between the end of the upper and lower curves
                self.UPPER_Y = np.append(self.UPPER_Y, (self.UPPER_Y[-1] + self.LOWER_Y[-1])/2)
                self.UPPER_X = np.append(self.UPPER_X, self.UPPER_X[-1])
                self.LOWER_Y = np.append(self.LOWER_Y, (self.UPPER_Y[-1] + self.LOWER_Y[-1])/2)
                self.LOWER_X = np.append(self.LOWER_X, self.LOWER_X[-1])
        
    def show(self, show_camber=False, figsize=(12,8), save=''):
        """
        Plots an airfoil using the airfoil data points
        foilname: name of airfoil
        show_camber: whether or not to show camber
        figsize: size of plot
        """
        # implement passing other arguments for fig and for ax into the method
        # implement save
        # implement plotting by interpolation

        fig, ax = plt.subplots(figsize=figsize)

        # this requires that 2 vectors are received, one fo the upper curve and another for the lower curve
        # the upper curve contains 2 vectors, X and Y. same with the lower curve
        ax.plot(self.UPPER_X, self.UPPER_Y, label = 'upper')
        ax.plot(self.LOWER_X, self.LOWER_Y, label = 'lower')

        TE_ax = fig.add_axes([0.65, 0.65, 0.2, 0.2])
        TE_ax.plot(self.UPPER_X[-5:], self.UPPER_Y[-5:])
        TE_ax.plot(self.LOWER_X[ :5], self.LOWER_Y[ :5])

        ax.set_aspect('equal', adjustable='datalim')
        ax.set_title(self.NAME)
        ax.set_xlabel("X")

        TE_ax.set_title("Trailing edge")
        # add text to show number of points used

        fig.show()

    def export_curve_to(self, format='solidworks_curve'):
        """
        Exports the airfoil coordinates to a file
        format: "SW txt" - the airfoil coordinates are saved as txt prepared to be used as a solidworks curve .txt
                "SW curve" - the airfoil coordinates are saved as a solidworks curve .sldcrv file
                "xml" - the airfoil coordinates are saved as xml file for xflr5 .xml
                "NURBS" - the airfoil coordinates are saved as a NURBS curve  
                "csv" - the airfoil coordinates are saved as a csv file .csv

        """
        if format == "solidworks_curve":
            file_ext = ".txt"
            self.EXPORT_FILENAME = self.NAME.replace(' ', '_') + file_ext
            with open(self.EXPORT_FILENAME, mode="w") as file:
                for x,y,z in zip(self.X, self.Y, self.Z):
                    if self.PLANE == 'xy' or "XY":
                        file.write(f"{str(x)}\t{str(y)}\t{str(z)}\n")
                    elif self.PLANE == 'xz' or 'XZ':
                        file.write(f"{str(x)}\t{str(z)}\t{str(y)}\n")
                    elif self.PLANE == 'yz' or 'YZ':
                        file.write(f"{str(y)}\t{str(z)}\t{str(x)}\n")
            
        elif format == "xml":
            file_ext = ".xml"
            self.EXPORT_FILENAME = self.NAME.replace(' ', '_') + file_ext

            # implement xml export
            # create an xml file with the airfoil coordinates
            # <?xml version="1.0"?>
            # <airfoil>
            #     <name>airfoil name</name>
            #     <points>
            #         <point>
            #             <x>0.0</x>
            #             <y>0.0</y>
            #             <z>0.0</z>
            #         </point>
            #     </points>
            # </airfoil>
            # save the xml file
        else:
            print(f"Invalid format: {format}")

        print(f'{self.NAME} saved as {format} file - {self.EXPORT_FILENAME}')
    
    # internal methods
    
    def __rotate(self, x_upper, y_upper, x_lower, y_lower, angle):
        """
        Rotate the airfoil by {incidence} degrees about the origin (0,0).
        
        Args:
            x_upper
            y_upper
            x_lower
            y_lower
            incidence: the angle in degrees to rotate the airfoil. +ve values rotate the airfoil CW and -ve values rotate the airfoil CCW
        
        Returns:
            tuple: upper_x, upper_y, lower_x, lower_y
        """
        print(f"rotate by {angle}")
        # this can only be called after the airfoil quarter chord has been moved to the origin as it rotates the
        # foil coordinates about the origin
        # if this method is caled on a foil that has been moved away from the origin, it should move the foil to the
        # origin, rotate the foil and then move the foil  back to its position
        # find a way to save the incidence angle of the airfoil

        angle_rad = np.deg2rad(angle)
        self.ROTATION_MATRIX = np.array([
            [ np.cos(angle_rad), -np.sin(angle_rad)],
            [ np.sin(angle_rad),  np.cos(angle_rad)],
            ])
        # rotate upper x and y values
        rotated_upper = np.dot(np.column_stack((x_upper, y_upper)), self.ROTATION_MATRIX)
        upper_x, upper_y = rotated_upper[:,0], rotated_upper[:,1]

        # rotate lower x and y values
        rotated_lower = np.dot(np.column_stack((x_lower, y_lower)), self.ROTATION_MATRIX)
        lower_x, lower_y = rotated_lower[:,0], rotated_lower[:,1]

        return upper_x, upper_y, lower_x, lower_y
    
    def __translate(self, x_upper, y_upper, x_lower, y_lower, dx, dy):
        """
        Moves the airfoil by a specific distance in the vertical and horizontal. 
        horizontal_offset: positive values move the airfoil rightward
        vertical_offset: positive values move the airfoil upward
        Args:
            x_upper, y_upper, x_lower, y_lower, dx=0, dy=0
        Returns:
            tuple: upper_x, upper_y, lower_x, lower_y
        """
        print(f"translate by {dx}, {dy}")
        self.TRANSLATION_MATRIX = np.array([
            [1, 0, dx],
            [0, 1, dy],
            [0, 0,  1]
        ])

        # augment coordinates with extra column of 1s
        upper_homogenous = np.vstack((x_upper, y_upper, np.ones_like(x_upper)))
        lower_homogenous = np.vstack((x_lower, y_lower, np.ones_like(x_lower)))

        # translate upper x and y values
        translated_upper = np.dot( self.TRANSLATION_MATRIX, upper_homogenous)
        upper_x, upper_y = translated_upper[0], translated_upper[1]

        # translate lower x and y values
        translated_lower = np.dot( self.TRANSLATION_MATRIX, lower_homogenous)
        lower_x, lower_y = translated_lower[0], translated_lower[1]

        return upper_x, upper_y, lower_x, lower_y
    
    def __scale(self, x_upper, y_upper, x_lower, y_lower, scale_factor):
        """
        Scales the airfoil by scale factor.
        Args:
            x_upper
            y_upper
            x_lower
            y_lower
            scale_factor: factor to scale the airfoil
        
        Returns:
            tuple: upper_x, upper_y, lower_x, lower_y
        """
        print(f"scale by {scale_factor}")
        self.SCALING_MATRIX = np.array([
            [scale_factor,     0],
            [0,     scale_factor]
        ])

        # rotate upper x and y values
        scaled_upper = np.dot(np.column_stack((x_upper, y_upper)), self.SCALING_MATRIX)
        upper_x, upper_y = scaled_upper[:,0], scaled_upper[:,1]

        # rotate lower x and y values
        scaled_lower = np.dot(np.column_stack((x_lower, y_lower)), self.SCALING_MATRIX)
        lower_x, lower_y = scaled_lower[:,0], scaled_lower[:,1]

        return upper_x, upper_y, lower_x, lower_y


class Airfoil:
    """
    Creates an airfoil object which can be rotated, moved, scaled. Base class for all airfoil types defined in the module

    More detailed description, purpose, usage, important details

    Attributes:
        QUARTER_CHORD (tuple (float, float)): description
        PATH (str): description
        NAME (str): description
        NUM_POINTS (int): description
        UPPER (np.ndarray): description
        LOWER (np.ndarray): description
        UPPER_X (np.ndarray): description
        UPPER_Y (np.ndarray): description
        LOWER_X (np.ndarray): description
        LOWER_Y (np.ndarray): description
        PLANE (str): description
        INCIDENCE (float): description
        X (np.ndarray): description
        Y (np.ndarray): description
        Z (np.ndarray): description
    
    Methods:
        calculate_quarter_chord(): Calcualtes the position of the quarter chord of the airfoil
        calculate_chord(): Calculates the length of the chord of the airfoil
        count_points(): count the number of points for the upper curve and lower curves
        center_foil(): centers the coordinates of the foil to make the quarter chord lie at (0,0)
        order_points(): Order the airfoil coordinates such that the data goes from LE over the upper surface to TE and then back to LE over the lower surface
        load(): Load the data from the dat file into the object and returns 2 matrices upper and lower, which contain 2 vectors each: X and Y
        scale_to(): Scales the airfoil to the given chord
        translate_to(): Translates the airfoil to a desired x, y position
        rotate_to(): Rotates the airfoil to a specific angle
        normalise(): Normalise the airfoil to a unit chord
        plane(): Specify and change the plane to be used when exporting to solidworks txt, which requires 3 columns of airfoil data depending on the plane in which the foil will be used
        flip(): Flip the airfoil vertically or horizontally
        close_TE(): CLoses the trailing edge. if the trailing edge is closed, it does nothing. If blend_TE is set to True, this will close the TE to a point, or otherwise make the TE a short vertical line
        show(): Plots an airfoil using the airfoil data points
        export_curve_to(): Exports the airfoil coordinates to a file that is readable by CAD software
    """
    def __init__(self, airfoil_path=None, airfoil_data=None, airfoil_name:str=None, plane:str="XY", incidence:float=None, chord:float=None, position:tuple=None, blend_trailing_edge=True):
        """
        Args:
            airfoil_path (str): path to airfoil dat file
            airfoil_data (list or np.ndarray): an iterable containing the vectors upper and lower of the coordinates of the airfoil. Only one of airfoil_path or airfoil_data can be used
            airfoil_name (str): the name of the foil. only used if airfoil_data is used and not airfoil_path
            plane (str): one of "XY", "YX", OR "YZ", "ZY" OR "XZ", "ZX". plane is defined horizontal first, then vertical. i.e XY has chord on X and thickness on Y. defaults to "XY"
            incidence (float): angle of incidence between chord and horizontal
            chord (float): chord value to scale the airfoil coordinates
            offset (float): the position offset of the airfoil (horizaontal, vertical)
            blend_trailing_edge (bool): whether to blend the TE or not. if True, TE closes to a single point. if False, TE remains as a vaertical line if it not closed and remains as is if it was closed
        """
        if airfoil_path:
            # if path to airfoil data is given
            self.PATH = airfoil_path
            self.NAME = None
            self.NUM_POINTS = None
            self.UPPER, self.LOWER = self.load(self.PATH)

        elif airfoil_data:
            # if airfoil coordinates are supplied
            self.PATH = None
            self.UPPER, self.LOWER = airfoil_data
            self.NAME = airfoil_name
            self.NUM_POINTS = self.count_points()
        
        self.UPPER_X, self.UPPER_Y = self.UPPER
        self.LOWER_X, self.LOWER_Y = self.LOWER

        self.close_TE(blend = blend_trailing_edge)

        self.PLANE = plane
        self.INCIDENCE = 0

        # center foil, then scale, then rotate, then translate
        # center the airfoil quarter_chord
        self.center_foil()

        # but if chord is given scale the foil to the given chord. 
        if chord:
            self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y = self.scale_to(chord)

        # rotate airfoil
        if incidence:
            self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y = self.rotate_to(incidence)

        # translate foil to desired position
        if position:
            self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y = self.translate_to(*position)
        
        self.X, self.Y = self.order_points()
        self.Z = np.zeros_like(self.X)

    def calculate_quarter_chord(self):
        """
        Calcualtes the position of the quarter chord of the airfoil and sets the self.QUARTER_CHORD parameter

        Returns:
            tuple: x, y
        """
        # self.QUARTER_CHORD =  (((self.UPPER_X[-1] - self.UPPER_X[0])/4)+self.UPPER_X[0], ((self.UPPER_Y[-1] - self.UPPER_Y[0])/4)+self.UPPER_Y[0])
        return (((self.UPPER_X[-1] - self.UPPER_X[0])/4)+self.UPPER_X[0], ((self.UPPER_Y[-1] - self.UPPER_Y[0])/4)+self.UPPER_Y[0])
    
    def calculate_chord(self):
        """
        Calculates the length of the chord of the airfoil

        Returns:
            float: chord
        """
        return np.sqrt((self.UPPER_X[-1] - self.UPPER_X[0])**2 + (self.UPPER_Y[-1] - self.UPPER_Y[0])**2)
    
    def count_points(self):
        """
        count the number of points for the upper curve and lower curves. This method is necessary if the airfoil_data is given instead of the path
        
        Args:
        Returns:
            tuple: num_upper, num_lower
        """
        pass

    def center_foil(self):
        '''centers the coordinates of the foil to make the quarter chord lie at (0,0)'''
        
        self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y = self.translate_to(0,0)

    def order_points(self):
        """
        Order the airfoil coordinates such that the data goes from LE over the upper surface to TE and then back to LE over the lower surface.

        Returns: 
            tuple: X, Y - X coordinates and Y coordinates of the foil from LE to TE and back to LE
        """
        # check if the data is in the correct order.
        # CORRECT ORDER: x values of upper curve goes from small to high and lower curve from high to small
        if (self.UPPER_X[0] < self.UPPER_X[-1]) and (self.LOWER_X[0] < self.LOWER_X[-1]):
            # Upper curve goes from small to high but lower cuve also goes from low to high. lower curve needs to reverse
            self.LOWER_X = np.flipud(self.LOWER_X)
            self.LOWER_Y = np.flipud(self.LOWER_Y)
            print('Lower curve reversed')
        
        # implement code to remove duplicate TE point
        # if last point of upper curve == first point of lower curve, remove the TE point
        # first point in lower curve
        if (self.UPPER_X[-1] == self.LOWER_X[0]) and (self.UPPER_Y[-1] == self.LOWER_Y[0]):
            lower_x = self.LOWER_X[1:]
            lower_y = self.LOWER_Y[1:]
        else:
            lower_x = self.LOWER_X[:]
            lower_y = self.LOWER_Y[:]

        # concatenate X and Y coordinates
        X = np.concatenate((self.UPPER_X, lower_x))
        Y = np.concatenate((self.UPPER_Y, lower_y))

        return X, Y

    def load(self, airfoil_path):
        """
        Load the data from the dat file into the object and returns 2 matrices upper and lower, which contain 2 vectors each: X and Y
        """
        raw = list()
        
        # claim and initialize variables
        num_points = None

        try:
            with open(airfoil_path) as airfoil_dat:
                contents = airfoil_dat.readlines()
        except Exception as e:
            logger.warn(f"Error -> {e}")
        else:
            for line in contents:
                line_content = line.strip().split() # strip whitespaces and split the line by spaces
                if len(line_content) < 1: # continue to next line if the line is Empty
                    continue
                
                # non-empty line starting with alphabet
                elif line_content[0].isalpha():
                    if self.NAME:
                        # if name has been defined already and another alphabet line is encountered, show warning and skip
                        print(f"Warning on line{contents.index(line)}, expected numeric, instead found:\n{' '.join(line_content)}")
                        continue
                    # If line contains alphabets, its the name line
                    self.NAME = ' '.join(line_content)

                elif float(line_content[0]) > 1:
                    # Number of data points
                    if self.NUM_POINTS:
                        # if num_points has been defined already and another line with large value is encountered,
                        # show warning and skip
                        print(f"Warning on line{contents.index(line)}, expected airfoil data, instead found:\n{' '.join(line_content)}")
                        continue
                    # num_points = list(map(int, list(map(float, line_content))))
                    num_points_upper = int(float(line_content[0]))
                    num_points_lower = int(float(line_content[1]))

                elif float(line_content[0]) <= 1:
                    raw.append(tuple(map(float, line_content))) # append Individual data point as a tuple of x and y values to raw
        
        # this assumes that a line is given as number of points in the file
        # use a conditional block to split the data at the TE, if the data started at the LE and vice versa 
        upper = np.array(raw[:num_points_upper])
        lower = np.array(raw[-num_points_lower:])
        return upper.T, lower.T

    def scale_to(self, chord):
        """
        Scales the airfoil to the given chord.
        Args:
            chord: the desired chord of the airfoil
        
        Returns:
            tuple: upper_x, upper_y, lower_x, lower_y
        """
        #calculate the scaling factor based on the current chord and the desired chord
        old_chord = self.calculate_chord()
        sc_factor = chord / old_chord
        
        # if quarter_chord is not at (0,0), you need to translate it to (0,0), perform scale operation and restore the translation
        quarter_chord = self.calculate_quarter_chord()
        if quarter_chord != (0.0, 0.0):
            x_u_t, y_u_t, x_l_t, y_l_t = self.__translate(self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y, -quarter_chord[0], -quarter_chord[1])
            x_u_s, y_u_s, x_l_s, y_l_s = self.__scale(x_u_t, y_u_t, x_l_t, y_l_t, sc_factor)
            x_u_o, y_u_o, x_l_o, y_l_o = self.__translate(x_u_s, y_u_s, x_l_s, y_l_s, quarter_chord[0], quarter_chord[1])
        else:
           x_u_o, y_u_o, x_l_o, y_l_o = self.__scale(self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y, sc_factor)

        return x_u_o, y_u_o, x_l_o, y_l_o

    def translate_to(self, x_position:float, y_position:float):
        """
        Translates the airfoil to a desired x, y position
        Args:
            x_position (float): desired x position of the foil
            y_position (float): desired y position of the foil

        Returns:
            tuple
        """
        # calculate the distance between the quarter chord and the desired position
        quarter_chord_x, quarter_chord_y = self.calculate_quarter_chord()

        dx = x_position - quarter_chord_x
        dy = y_position - quarter_chord_y
        x_u_t, y_u_t, x_l_t, y_l_t = self.__translate(self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y, dx, dy)

        return x_u_t, y_u_t, x_l_t, y_l_t

    def rotate_to(self, angle):
        """
        Rotates the airfoil to a specific angle
        Args:
            angle
        
        Returns:
            tuple
        """
        da = angle - self.INCIDENCE

        x_u_r, y_u_r, x_l_r, y_l_r = self.__rotate(self.UPPER_X, self.UPPER_Y, self.LOWER_X, self.LOWER_Y, da)

        # update foil incidence angle
        self.INCIDENCE = angle

        return x_u_r, y_u_r, x_l_r, y_l_r
    
    def normalise(self):
        """
        Normalise the airfoil to a unit chord
        """
        # consider normalise after the foil has been offset, which will require a more robust implementation
        pass

    def plane(self, plane):
        """
        Specify and change the plane to be used when exporting to solidworks txt, which requires 3 columns
        of airfoil data depending on the plane in which the foil will be used
        """
        # if plane is xy or XY, X data maps to X column and Y data maps to Y column
        # if plane is yx or YX, X data maps to Y column and Y data maps to X column
        # if plane is xz or XZ, X data maps to X column and Y data maps to Z column
        # if plane is zx or ZX, X data maps to Z column and Y data maps to X column
        # if plane is yz or YZ, X data maps to Y column and Y data maps to Z column
        # if plane is zy or ZY, X data maps to Z column and Y data maps to Y column
        # merge the implementation of the plane and flip methods
        pass

    def flip(self, axis="hor"):
        """
        Flip the airfoil vertically or horizontally
        """
        pass

    def close_TE(self, blend):
        """
        CLoses the trailing edge. if the trailing edge is closed, it does nothing.
        If blend_TE is set to True, this will close the TE to a point, or otherwise make the TE a short vertical line
        Short TE line is preferable for hot-wire manufacturing but choice is left to user
        """
        ### does this implementation add a new point to the trailing edge or does it simply move the last point to the middle of the trailing edge?
        # also ensure that the line does not exceed a certain threshold size for very large scaled foils
        # call this function before any transformation
        # if x_upper[-1] == y_upper[-1]
        
        if (self.UPPER_X[-1] != self.LOWER_X[-1]):
            self.UPPER_X[-1] = self.LOWER_X[-1] = (self.UPPER_X[-1] + self.LOWER_X[-1])/2

        if self.UPPER_Y[-1] != self.LOWER_Y[-1]:
            if blend:
                self.UPPER_Y[-1] = self.LOWER_Y[-1] = (self.UPPER_Y[-1] + self.LOWER_Y[-1])/2
            else:
                # close TE as a line instead of to a point. simply add a point between the end of the upper and lower curves
                self.UPPER_Y = np.append(self.UPPER_Y, (self.UPPER_Y[-1] + self.LOWER_Y[-1])/2)
                self.UPPER_X = np.append(self.UPPER_X, self.UPPER_X[-1])
                self.LOWER_Y = np.append(self.LOWER_Y, (self.UPPER_Y[-1] + self.LOWER_Y[-1])/2)
                self.LOWER_X = np.append(self.LOWER_X, self.LOWER_X[-1])
        
    def show(self, show_camber=False, figsize=(12,8), save=''):
        """
        Plots an airfoil using the airfoil data points
        foilname: name of airfoil
        show_camber: whether or not to show camber
        figsize: size of plot
        """
        # implement passing other arguments for fig and for ax into the method
        # implement save
        # implement plotting by interpolation

        fig, ax = plt.subplots(figsize=figsize)

        # this requires that 2 vectors are received, one fo the upper curve and another for the lower curve
        # the upper curve contains 2 vectors, X and Y. same with the lower curve
        ax.plot(self.UPPER_X, self.UPPER_Y, label = 'upper')
        ax.plot(self.LOWER_X, self.LOWER_Y, label = 'lower')

        TE_ax = fig.add_axes([0.65, 0.65, 0.2, 0.2])
        TE_ax.plot(self.UPPER_X[-5:], self.UPPER_Y[-5:])
        TE_ax.plot(self.LOWER_X[ :5], self.LOWER_Y[ :5])

        ax.set_aspect('equal', adjustable='datalim')
        ax.set_title(self.NAME)
        ax.set_xlabel("X")

        TE_ax.set_title("Trailing edge")
        # add text to show number of points used

        fig.show()

    def export_curve_to(self, format='solidworks_curve'):
        """
        Exports the airfoil coordinates to a file
        format: "SW txt" - the airfoil coordinates are saved as txt prepared to be used as a solidworks curve .txt
                "SW curve" - the airfoil coordinates are saved as a solidworks curve .sldcrv file
                "xml" - the airfoil coordinates are saved as xml file for xflr5 .xml
                "NURBS" - the airfoil coordinates are saved as a NURBS curve  
                "csv" - the airfoil coordinates are saved as a csv file .csv

        """
        if format == "solidworks_curve":
            file_ext = ".txt"
            self.EXPORT_FILENAME = self.NAME.replace(' ', '_') + file_ext
            with open(self.EXPORT_FILENAME, mode="w") as file:
                for x,y,z in zip(self.X, self.Y, self.Z):
                    if self.PLANE == 'xy' or "XY":
                        file.write(f"{str(x)}\t{str(y)}\t{str(z)}\n")
                    elif self.PLANE == 'xz' or 'XZ':
                        file.write(f"{str(x)}\t{str(z)}\t{str(y)}\n")
                    elif self.PLANE == 'yz' or 'YZ':
                        file.write(f"{str(y)}\t{str(z)}\t{str(x)}\n")
            
        elif format == "xml":
            file_ext = ".xml"
            self.EXPORT_FILENAME = self.NAME.replace(' ', '_') + file_ext

            # implement xml export
            # create an xml file with the airfoil coordinates
            # <?xml version="1.0"?>
            # <airfoil>
            #     <name>airfoil name</name>
            #     <points>
            #         <point>
            #             <x>0.0</x>
            #             <y>0.0</y>
            #             <z>0.0</z>
            #         </point>
            #     </points>
            # </airfoil>
            # save the xml file
        else:
            print(f"Invalid format: {format}")

        print(f'{self.NAME} saved as {format} file - {self.EXPORT_FILENAME}')
    
    # Mangled internal methods
    
    def __rotate(self, x_upper, y_upper, x_lower, y_lower, angle):
        """
        Rotate the airfoil by {incidence} degrees about the origin (0,0).
        
        Args:
            x_upper
            y_upper
            x_lower
            y_lower
            incidence: the angle in degrees to rotate the airfoil. +ve values rotate the airfoil CW and -ve values rotate the airfoil CCW
        
        Returns:
            tuple: upper_x, upper_y, lower_x, lower_y
        """
        print(f"rotate by {angle}")
        # this can only be called after the airfoil quarter chord has been moved to the origin as it rotates the
        # foil coordinates about the origin
        # if this method is caled on a foil that has been moved away from the origin, it should move the foil to the
        # origin, rotate the foil and then move the foil  back to its position
        # find a way to save the incidence angle of the airfoil

        angle_rad = np.deg2rad(angle)
        self.ROTATION_MATRIX = np.array([
            [ np.cos(angle_rad), -np.sin(angle_rad)],
            [ np.sin(angle_rad),  np.cos(angle_rad)],
            ])
        # rotate upper x and y values
        rotated_upper = np.dot(np.column_stack((x_upper, y_upper)), self.ROTATION_MATRIX)
        upper_x, upper_y = rotated_upper[:,0], rotated_upper[:,1]

        # rotate lower x and y values
        rotated_lower = np.dot(np.column_stack((x_lower, y_lower)), self.ROTATION_MATRIX)
        lower_x, lower_y = rotated_lower[:,0], rotated_lower[:,1]

        return upper_x, upper_y, lower_x, lower_y
    
    def __translate(self, x_upper, y_upper, x_lower, y_lower, dx, dy):
        """
        Moves the airfoil by a specific distance in the vertical and horizontal. 
        horizontal_offset: positive values move the airfoil rightward
        vertical_offset: positive values move the airfoil upward
        Args:
            x_upper, y_upper, x_lower, y_lower, dx=0, dy=0
        Returns:
            tuple: upper_x, upper_y, lower_x, lower_y
        """
        print(f"translate by {dx}, {dy}")
        self.TRANSLATION_MATRIX = np.array([
            [1, 0, dx],
            [0, 1, dy],
            [0, 0,  1]
        ])

        # augment coordinates with extra column of 1s
        upper_homogenous = np.vstack((x_upper, y_upper, np.ones_like(x_upper)))
        lower_homogenous = np.vstack((x_lower, y_lower, np.ones_like(x_lower)))

        # translate upper x and y values
        translated_upper = np.dot( self.TRANSLATION_MATRIX, upper_homogenous)
        upper_x, upper_y = translated_upper[0], translated_upper[1]

        # translate lower x and y values
        translated_lower = np.dot( self.TRANSLATION_MATRIX, lower_homogenous)
        lower_x, lower_y = translated_lower[0], translated_lower[1]

        return upper_x, upper_y, lower_x, lower_y
    
    def __scale(self, x_upper, y_upper, x_lower, y_lower, scale_factor):
        """
        Scales the airfoil by scale factor.
        Args:
            x_upper
            y_upper
            x_lower
            y_lower
            scale_factor: factor to scale the airfoil
        
        Returns:
            tuple: upper_x, upper_y, lower_x, lower_y
        """
        print(f"scale by {scale_factor}")
        self.SCALING_MATRIX = np.array([
            [scale_factor,     0],
            [0,     scale_factor]
        ])

        # rotate upper x and y values
        scaled_upper = np.dot(np.column_stack((x_upper, y_upper)), self.SCALING_MATRIX)
        upper_x, upper_y = scaled_upper[:,0], scaled_upper[:,1]

        # rotate lower x and y values
        scaled_lower = np.dot(np.column_stack((x_lower, y_lower)), self.SCALING_MATRIX)
        lower_x, lower_y = scaled_lower[:,0], scaled_lower[:,1]

        return upper_x, upper_y, lower_x, lower_y

class NACA4DigitFoil(Airfoil):
    """
    NACA 4 digit airfoil, a subclass of Airfoil.
    (pmtt e.g. 4412)

    Arguments:
        p: {maximum camber} in % of the chord
        m: {location of maximum camber} in % of the chord
        tt: last 2 digits representing {thickness} in % of the chord
    """
    def __init__(self, naca_digits, n_points, **kwargs):
        """
        Create an airfoil object from a NACA 4-digit series definition

        Args:
            naca_digits: String like '4412'
            n_points: Total number of points used to create the airfoil
            kwargs: additional arguments for the Airfoil object

        Returns:
            Airfoil: New airfoil instance
        """
        re_4digits = re.compile(r"^\d{4}$")
        self.NUM_POINTS = n_points

        if re_4digits.match(naca_digits):
            self.p = float(naca_digits[0])/10
            self.m = float(naca_digits[1])/100
            self.t = float(naca_digits[2:4])/100
        else:
            raise Exception("Identifier not recognised as valid NACA 4 definition")
        super(self).__init__(airfoil_data = self.generate(), airfoil_name=self.__name__)
    
    def generate(self):
        """
        Returns:
            upper, lower: upper contains (x,y), lower contains (x,y)
        """
        self.x = np.linspace(0, 1, self.NUM_POINTS)
        yt = self.thickness(self.x, self.t)

        yc = self.camber(self.p, self.m, self.x, self.p, self.m)
        dyc = self.camber_gradient(self.x, self.p, self.m)
        theta = np.arctan(dyc)

        x_upper = self.x - yt*np.sin(theta)
        y_upper = yc + yt*np.cos(theta)
        x_lower = self.x + yt*np.sin(theta)
        y_lower = yc - yt*np.cos(theta)

        upper = np.array([x_upper, y_upper])
        lower = np.array([x_lower, y_lower])
        
        return np.array([upper, lower])
        
    def thickness(self, x, t):
        """
        Calculate the y coordinates for the upper and lower curves
        Arguments:
            x: x coordinates
            t: thickness parameter from airfoil definition
        """
        # if the thickness is greater than 20%, calculate the
        # ordinates for the model with thickness-chord ratio
        # of 0.2 and multiply by the ratio (t/c)/0.2
        a0 = 0.2969
        a1 = -0.1260
        a2 = -0.3516
        a3 = 0.2843
        a4 = -0.1015

        yt = 5*t * (a0*np.sqrt(x) + a1*x + a2*x**2 + a3*x**3 + a4*x**4)
        return yt
    
    def camber(self, x, p, m):
        """
        Calculate the y coordinates of the camber line

        Arguments:
            x:
            p:
            m:

        Returns:
            array: y coordinates of the camber line
        """
        return np.where(x < p, (m/(p**2)) * (2*p*x - x**2), (m/((1 - p)**2)) * ((1 - 2*p) + 2*p*x - x**2))

    def camber_gradient(self, x, p, m):
        """
        Calculate the gradient of the camber line.

        Arguments:
            x:
            p:
            m:

        Returns:
            array: gradient of the camber line
        """
        return np.where(x < p, (m/p**2)*(2*p*x - x**2), (2*m/(1 - p)**2)*(p - x))

class NACA5DigitFoil(Airfoil):
    def __init__(self, naca_digits:str, n_points, **kwargs):
        self.NUM_POINTS = int(n_points) # ensures that the number of points is an integer

        self.l = int(naca_digits[0]) * 0.15
        self.p = int(naca_digits[1]) * 0.05
        self.s = int(naca_digits[2])
        self.t = int(naca_digits[3:]) / 100
        super(self).__init__(airfoil_data = self.generate(), airfoil_name=self.__name__)

    def __non_reflexed_camber(self, x):
        # exp_a = (k1/6) * (x**3 - 3*r*x**2 + r**2*(3-r)*x)
        # exp_b = ((k1*r**3)/6)*(1-x)
        # return np.where(x<r, exp_a, exp_b)
        pass
    
    def __reflexed_camber(self, x):
        # exp_a = (k1/6) * ((x/c - r)**3 - (k2/k1)*(x/c)*(1-r)**3 - (x/c)*r**3 + r**3)
        # exp_b = (k1/6)*((k2/k1) *(x/c - r)**3 - (k2/k1)*(x/c)*(1-r)**3 - (x/c)*r**3 + r**3)
        # return np.where((x/c)<=r, exp_a, exp_b)
        pass
    
    def camber_gradient(self, x, k1, r):
        pass

    def thickness(self, x):
        pass

class NACA6DigitFoil(Airfoil):
    def __init__(self):
        pass

