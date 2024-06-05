import pandas as pd

# Load the CSV file with the correct delimiter and column names
file_path = 'data/DRUG-AE.csv'
column_names = ['ID', 'Description', 'Adverse Event', 'Start Time', 'End Time', 'Drug Name', 'Start Time 2', 'End Time 2']
data_corrected = pd.read_csv(file_path, delimiter='|', names=column_names)

# Keep only relevant columns 'ID', 'Description', and 'Adverse Event'
df_relevant_corrected = data_corrected[['ID', 'Description', 'Adverse Event']]

# Group by 'ID' and 'Description', and aggregate 'Adverse Event' into lists
df_grouped_corrected = df_relevant_corrected.groupby(['ID', 'Description']).agg({'Adverse Event': lambda x: list(x)}).reset_index()
df_grouped_corrected.rename(columns={'Adverse Event': 'AE', 'Description': 'text'}, inplace=True)

# Drop the 'ID' column
df_final = df_grouped_corrected.drop(columns=['ID'])

# Display the processed dataframe
print(df_final)

# Optionally, save the processed dataframe to a new CSV file
df_final.to_csv('data/processed_ade_codes.csv', index=False)

