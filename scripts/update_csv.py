import pandas as pd
from tqdm import tqdm
import argparse

def process_user_data(input_path, output_path):
    # Load the provided CSV file
    data_original = pd.read_csv(input_path)

    # Save the original Date column
    original_dates = data_original['Date']

    # Convert the 'Date' column from UNIX timestamp to datetime and then to GMT+2
    data_original['Date'] = pd.to_datetime(data_original['Date'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Etc/GMT-2')

    # Sort the data by SessionID and Date
    data_original = data_original.sort_values(by=['SessionID', 'Date']).reset_index(drop=True)

    max_vies = 2

    # Helper function to update series and lives
    def update_series_and_lives(session_id, date, pratique, user_stats, previous_date):
        if session_id not in user_stats:
            user_stats[session_id] = {'serie': 0, 'vies': 2, 'last_practiced_date': None}
        
        stats = user_stats[session_id]
        serie = stats['serie']
        vies = stats['vies']
        last_practiced_date = stats['last_practiced_date']
        
        # Check if the current date is consecutive to the last practiced date
        if last_practiced_date is not None and (date - last_practiced_date).days == 1:
            if pratique:
                serie += 1
                if serie % 5 == 0 and vies < max_vies:
                    vies += 1
            else:
                if vies > 0:
                    vies -= 1
                else:
                    serie = 0
                    vies = max_vies
        else:
            if pratique:
                serie = 1
            else:
                if vies > 0:
                    vies -= 1
                else:
                    serie = 0
                    vies = max_vies
        
        # Reset series and lives if vies are negative
        if vies < 0:
            serie = 0
            vies = max_vies
        
        if pratique:
            user_stats[session_id] = {'serie': serie, 'vies': vies, 'last_practiced_date': date}
        else:
            user_stats[session_id] = {'serie': serie, 'vies': vies, 'last_practiced_date': last_practiced_date}
        
        return {'SessionID': session_id, 'Date': date, 'Serie': serie, 'Vies': vies}

    # Group data by user and date
    users_grouped = data_original.groupby(['SessionID', data_original['Date'].dt.date])

    # Initialize a dictionary to store series and lives for each user
    user_stats = {}

    # Calculate series and lives for each user
    calculations = []

    for (session_id, date), group in tqdm(users_grouped, desc="Processing users"):
        pratique = False
        
        # Check if the user has completed the required exercises for the day
        allonge_valid = False
        assis_valid = False
        
        # Check if the user has completed 2 exercises of 5' or 1 exercise of 10' for allongé and assis
        for pos in ['Allonge', 'Assis']:
            niveau_1_count = group[(group['Niveau'] == 1) & (group[pos] == True)].shape[0]
            niveau_2_count = group[(group['Niveau'] == 2) & (group[pos] == True)].shape[0]
            
            if (niveau_1_count >= 2) or (niveau_2_count >= 1):
                if pos == 'Allonge':
                    allonge_valid = True
                elif pos == 'Assis':
                    assis_valid = True
        
        if allonge_valid and assis_valid:
            pratique = True
        
        previous_date = user_stats[session_id]['last_practiced_date'] if session_id in user_stats else None
        calculation = update_series_and_lives(session_id, date, pratique, user_stats, previous_date)
        calculations.append(calculation)

    # Convert calculations to DataFrame
    calculated_df = pd.DataFrame(calculations)

    # Merge the calculated series with the original data
    data_original['Date_Date'] = data_original['Date'].dt.date
    merged_df = data_original.merge(calculated_df, left_on=['SessionID', 'Date_Date'], right_on=['SessionID', 'Date'], how='left', suffixes=('', '_Calculated'))

    # Add the correctly calculated series to the original dataframe
    final_df = data_original.copy()
    final_df['Serie'] = merged_df['Serie']

    # Restore the original Date column
    final_df['Date'] = original_dates

    # Handle formattedDate column
    final_df['formattedDate'] = final_df['formattedDate'].fillna(final_df['Date'].apply(lambda x: pd.to_datetime(x, unit='s').strftime('%Y-%m-%d')))

    # Drop unnecessary columns
    final_df = final_df.drop(columns=['Date_Date'])

    # Sort the final dataframe by user and date
    final_df = final_df.sort_values(by=['SessionID', 'Date']).reset_index(drop=True)

    # Select columns to match the original dataframe and add the calculated series column
    final_columns = ['Date', 'Niveau', 'Allonge', 'Assis', 'SessionID', 'formattedDate', 'Serie']
    final_df = final_df[final_columns]

    # Save the final dataframe to a CSV file
    final_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process user data.')
    parser.add_argument('input_path', type=str, help='Path to the input CSV file')
    parser.add_argument('output_path', type=str, help='Path to the output CSV file')
    args = parser.parse_args()

    process_user_data(args.input_path, args.output_path)
