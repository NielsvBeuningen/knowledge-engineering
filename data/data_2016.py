import pandas as pd

# Gathered Data From: https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/3218.02016-17?OpenDocument

# Path to the .xls file
file_path = r"C:\Users\wfeij\Documents\pop_estimates_sa2_2016-2017.xlsx"

# Load the Excel file
xls = pd.ExcelFile(file_path)

# List to hold DataFrames for each sheet
sheet_list = []

# Iterate through each sheet and read it into a DataFrame
for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet_name)
    sheet_list.append(df)

# Concatenate all DataFrames
df = pd.concat(sheet_list, ignore_index=True)

df = df.rename({"SA2 code": "SA2_CODE_2016",
        "SA2 name": "SA2_NAME_2016",
        "Area (km2)": "AREA_SQKM",
        "2016pr":"NR_OF_PEOPLE_2016",
        },
        axis=1
     )


tot_nr_people = df["NR_OF_PEOPLE_2016"].sum() # 24.19 on Google


df["SA2_5DIG16"]              = [str(i)[0]+str(i)[-4:] for i in df["SA2_CODE_2016"]]
df["NR_OF_PEOPLE_2016_%"]     = [round((nr/tot_nr_people)*100,2) for nr in df["NR_OF_PEOPLE_2016"]]
df["POPULATION_DENSITY_2016"] = [df.loc[i,"NR_OF_PEOPLE_2016"]/df.loc[i,"AREA_SQKM"] for i in range(len(df))]


columns = [
    'SA2_CODE_2016',
    "SA2_NAME_2016",
    'SA2_5DIG16',
    'AREA_SQKM',
    'NR_OF_PEOPLE_2016',
    'NR_OF_PEOPLE_2016_%',
    'POPULATION_DENSITY_2016',
]

SA2PopulationData2016 = df[columns]

SA2PopulationData2016.to_csv("processed/SA2PopulationData2016.csv",index=False)
