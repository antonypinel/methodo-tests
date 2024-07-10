import pandas as pd
from tqdm import tqdm

def calculate_series(data):

    series = 0
    lives = 2
    max_lives = 2
    
    data['serie'] = 0
    grouped = data.groupby(['formattedDate', 'SessionID'])
    
    processed_groups = []
    for name, group in tqdm(grouped, desc="Processing", total=len(grouped)):
        valid_session = False

        # Vérification si la session est valide (deux exercices de 5 minutes ou un exercice de 10 minutes)
        if (group['Niveau'] == 1).sum() >= 2 or (group['Niveau'] == 2).sum() >= 1:
            valid_session = True

        if valid_session:
            series += 1
        else:
            lives -= 1

        # Vérification si les vies sont épuisées
        if lives < 0:
            series = 0
            lives = max_lives

        # Régénération d'une vie tous les 5 jours consécutifs de pratique
        if series > 0 and series % 5 == 0:
            lives = min(lives + 1, max_lives)

        group['serie'] = series
        processed_groups.append(group)

    # Concaténer tous les groupes traités
    processed_data = pd.concat(processed_groups).reset_index(drop=True)
    
    return processed_data

if __name__ == "__main__":
    input_csv_path = 'data/input.csv'
    output_csv_path = 'data/output.csv'

    print(f"Loading data from {input_csv_path}...")
    data = pd.read_csv(input_csv_path)

    print("Calculating series...")
    updated_data = calculate_series(data)

    print(f"Saving updated data to {output_csv_path}...")

    # Convertir 'Niveau' en entier en conservant uniquement la partie entière pour les valeurs non-nulles
    updated_data['Niveau'] = updated_data['Niveau'].apply(lambda x: int(str(x).split('.')[0]) if pd.notnull(x) else 0)

    updated_data.to_csv(output_csv_path, index=False, quotechar='"', quoting=1)

    print("Done")
