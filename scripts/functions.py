"""
Helper functions
"""
import os
from pathlib import Path
from bs4 import BeautifulSoup
import re

# from ..globals import AIRFOIL_PATH

def get_foils_from_dir(data_path):
    files = [f for f in os.listdir(data_path) if os.path.isfile(f)]
    return files

def get_save_airfoils():
    try:
        import urllib.request as urllib2
    except ImportError:
        import urllib2

    # Base filepath for the UIUC airfoil website (used for accessing .dat files)
    baseFlpth = "https://m-selig.ae.illinois.edu/ads/"

    # Open the webpage and create the soup
    html_page = urllib2.urlopen("https://m-selig.ae.illinois.edu/ads/coord_database.html")		
    soup      = BeautifulSoup(html_page,'lxml')	

    # Loop over all relevant files and save each one
    counter = 1									# Iteration counter
    links = []									# Initialize list of links for appending

    # Loop over all appropriate links on webpage
    for link in soup.find_all('a',attrs={'href': re.compile('\.dat', re.IGNORECASE)}):
        links.append(link.get('href'))			# Append the link to the list
        # Get the data from the webpage, and save it to the save data file as the link name
        urllib2.urlretrieve(baseFlpth+link.get('href'), link.get('href').rsplit('/',1)[-1])	
        print("Saving file %i" %counter)		# Indicate the link that we are currently saving
        counter += 1							# Increment the counter


if __name__ == "__main__":
    airfoils = get_foils_from_dir()
    print(airfoils)

