import pandas as pd
from tqdm import tqdm

# Fonction pour calculer la série et les vies
def calculate_series_and_lives(df):
    df['serie'] = 0
    df['lives'] = 2

    # Trier les données par SessionID et Date pour un traitement séquentiel correct
    df.sort_values(by=['SessionID', 'Date'], inplace=True)

    previous_session_id = None
    previous_date = None
    consecutive_days = 0
    lives = 2
    serie = 0

    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing"):
        current_date = pd.to_datetime(row['Date'])
        current_session_id = row['SessionID']

        # Vérifier si nous avons changé de session utilisateur
        if current_session_id != previous_session_id:
            previous_date = None
            consecutive_days = 0
            lives = 2
            serie = 0

        if previous_date is not None:
            days_difference = (current_date - previous_date).days
            if days_difference == 1:
                consecutive_days += 1
                if consecutive_days % 5 == 0 and lives < 2:
                    lives += 1
            elif days_difference > 1:
                days_without_practice = days_difference - 1
                lives -= days_without_practice
                if lives < 0:
                    lives = 0
                serie = 0
                consecutive_days = 0

        if row['Allonge'] or row['Assis']:
            if lives > 0:
                serie += 1
            else:
                serie = 1
                lives = 2
        else:
            lives -= 1
            if lives < 0:
                lives = 0
            serie = 0

        if lives == 0:
            serie = 0
            lives = 2

        df.at[index, 'serie'] = serie
        df.at[index, 'lives'] = lives

        previous_date = current_date
        previous_session_id = current_session_id

    return df

# Lire les données d'entrée
input_file_path = '../data/input.csv'
output_file_path = '../data/export.csv'

df = pd.read_csv(input_file_path)

# Calculer les colonnes 'serie' et 'lives'
df = calculate_series_and_lives(df)

# Sauvegarder les résultats dans le fichier de sortie
df.to_csv(output_file_path, index=False)

print(f"Output saved to {output_file_path}")
