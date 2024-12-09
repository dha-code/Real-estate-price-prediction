def replace_epc(x):
    """
    Function to replace EPC score (string) to numerical value
    """
    if x == 'A++' or x == 'A+' or x == 'A':
        return 1
    elif x == 'B' or x == 'C' or x == 'C_A':
        return 2
    elif x == 'D' or x == 'E':
        return 3
    elif x == 'F' or x == 'G':
        return 5
    else:
        return 2.5
    
def replace_build_state(x):
    """
    Function to replace Building state (string) to numerical value
    """
    if x == 'GOOD':
        return 1
    elif x == 'AS_NEW' or x == 'JUST_RENOVATED':
        return 2
    elif x == 'TO_RENOVATE' or x == 'TO_BE_DONE_UP' or x == 'TO_RESTORE':
        return 0
    else:
        return 0.75

def categorize_property(property_type):
    """
    Function to replace Property type (string) to numerical value
    """
    house = ["HOUSE","TOWN_HOUSE","BUNGALOW","LOFT","CHALET"]
    apartment = ["APARTMENT","GROUND_FLOOR","TRIPLEX","PENTHOUSE","DUPLEX"]
    small = ["FLAT_STUDIO","SERVICE_FLAT","KOT"]
    
    if property_type in house:
        return 2
    elif property_type in apartment:
        return 1
    elif property_type in small:
        return 0
    else:
        return 4
    
def get_region(x):
    """
    Function to add a column Region based on zip code
    """
    if x >=1000 and x <=1200:
        return 1
    elif (x >=1500 and x<=3999) or (x >= 8000 and x <= 9999):
        return 2
    else:
        return 3