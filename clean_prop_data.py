import pandas as pd
from utils import preprocess

# Import data scraped from immoweb, external data on latitude longitude of zip codes and additional data
immo_df = pd.read_csv('./data/PropertyData.csv')
be_zip =  pd.read_csv('./data/zipcode-belgium.csv', header=None, usecols = [0,2,3])
income = pd.read_csv('./data/zip_info.txt',sep="\t")

# Drop duplicate property data
immo_df = immo_df.drop_duplicates()

# Calculate the age of the property based on the construction year
immo_df.loc[immo_df["Construction year"] >= 2024, "Construction year"] = 2024
immo_df.loc[ immo_df["Construction year"].isna() & (immo_df["Price"] <= 250000), "Construction year"] = 1975
immo_df.loc[ immo_df["Construction year"].isna() & (immo_df["Price"] >= 500000), "Construction year"] = 1995
immo_df.loc[immo_df["Construction year"].isna(), "Construction year"] = 1985
immo_df["Age"] = 2024 - immo_df["Construction year"]

# Ensure the zipcodes are onli in BE region
immo_df["Locality"] = immo_df["Locality"].str[0:4]
immo_df['Locality'] = immo_df['Locality'].astype(int)
immo_df.drop(immo_df[immo_df["Locality"] > 9999].index, inplace = True)

# Check for additional duplicates and drop few columns 
immo_df.drop_duplicates(subset=["Locality","Property type","Price","Living area","Bedrooms","Bathrooms","Land surface"], inplace=True)
immo_df.drop(columns=["Type sale","Garden Area","Equipped kitchen","Construction year"], axis=1, inplace=True)
immo_df.dropna(subset=["Locality","Price"], inplace=True)

# Drop property outliers based on living area, land surface and price 
immo_df.drop(immo_df[immo_df['Living area'] > 1200].index, inplace = True)
immo_df.drop(immo_df[immo_df['Land surface'] >= 20000].index, inplace = True)
immo_df.drop(immo_df[immo_df["Price"] < 99000].index, inplace = True)
immo_df.drop(immo_df[immo_df["Price"]>= 2000000].index, inplace = True)

# Fill NA values of facades and living area based on logic
immo_df.loc[ immo_df["Facades"].isna() & (immo_df["Property type"] == "HOUSE"), "Facades"] = 3.0
immo_df.loc[ immo_df["Facades"].isna() & (immo_df["Property type"] == "APARTMENT"), "Facades"] = 2.0
immo_df.loc[ immo_df["Living area"].isna() & (immo_df["Property type"] == "HOUSE"), "Living area"] = 212
immo_df.loc[ immo_df["Living area"].isna() & (immo_df["Property type"] == "APARTMENT"), "Living area"] = 99

# Check the bedroom and bathroom count 
immo_df["Bedrooms"] = immo_df["Bedrooms"].apply(lambda x: x if x<8 else 8)
immo_df["Bathrooms"] = immo_df["Bathrooms"].fillna(1.5)
immo_df["Bathrooms"] = immo_df["Bathrooms"].apply(lambda x: x if x<5 else 5)

# Clean up terrace area
immo_df.loc[(immo_df["Terrace"] == 0) & immo_df["Terrace Area"].isna(), "Terrace Area"] = 0
immo_df.loc[immo_df["Terrace Area"]>100, 'Terrace Area'] = 100 
immo_df["Terrace Area"] = immo_df["Terrace Area"].fillna(15)

# Process the latitude longitude information which was imported
be_zip.columns = ["Locality","Longitude","Latitude"]
be_zip['Locality'] = be_zip['Locality'].astype(int)
be_zip.drop_duplicates(subset=["Locality"], inplace=True)

# Merge the new information with the property data
immo_gps = pd.merge(immo_df, be_zip, on='Locality', how='left')
immo_gps.dropna(subset=["Longitude"], inplace=True)
    
# Apply the label encoding functions defined in utils to the respective columns
immo_gps["EPC score"] = immo_gps["EPC score"].apply(preprocess.replace_epc)
immo_gps["Building state"] = immo_gps["Building state"].apply(preprocess.replace_build_state)
immo_gps["Region"] = immo_gps["Locality"].apply(preprocess.get_region)
immo_gps["Subtype"] = immo_gps["Subtype"].apply(preprocess.categorize_property)

# Categorise the type of the property  
immo_gps["Property type"] = immo_gps["Property type"].map({"HOUSE":1,"APARTMENT":0})

# Merge the income, tax and population density columns from external data
income['Locality'] = income['Locality'].astype(int)
immo_inco = pd.merge(immo_gps, income, on='Locality', how='left')

# Ensure that all columns have non-null values
print(immo_inco.info())

# Select subset of columns that will be used for model training and testing
immo_knn = immo_inco[["Property type","Subtype","Price","Age","Bedrooms","Living area","Bathrooms",
                     "Terrace Area","EPC score","Land surface","Taxes", "Population Density",
                     "Facades","Building state","Region","Latitude","Longitude","Income"]] 

# Write the selected columns to a new file
immo_knn.to_csv("./data/KNNInput.txt",index=False)