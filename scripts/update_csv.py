import pandas as pd
from tqdm import tqdm
from datetime import datetime

# Charger les données
df = pd.read_csv('../data/input.csv')

# Filtrer les lignes où SessionID est null
df = df[df['SessionID'].notna()]

# Convertir la colonne 'Date' de timestamp à datetime
df['formattedDate'] = pd.to_datetime(df['Date'], unit='s')
df['formattedDate'] = df['formattedDate'].dt.strftime('%Y-%m-%d')

# Initialiser les colonnes pour les séances et les vies
df['serie'] = 0
df['vies'] = 2

# Trier les données par SessionID et date
df.sort_values(by=['SessionID', 'formattedDate'], inplace=True)

import pandas as pd

def calculate_daily_practice(df):
    """
    Calcul la série de pratiques et gère les vies selon les conditions suivantes:
    - Une pratique est comptée si 'Allonge' et 'Assis' sont tous les deux True pour un jour.
    - Une série est incrémentée pour chaque jour consécutif de pratique complète.
    - Une vie est décomptée si aucune pratique n'est complétée et des vies sont disponibles.
    - La série est réinitialisée à zéro si aucune pratique n'est complétée et aucune vie n'est disponible.
    - Les vies sont réinitialisées à deux après une rupture de série.
    - Une vie est regagnée tous les 5 jours consécutifs de pratique, avec un maximum de 2 vies.
    """
    results = []
    streak = 0
    lives = 2  # Commencer avec 2 vies par défaut

    # Tri par date pour s'assurer que le traitement est séquentiel
    df.sort_values('formattedDate', inplace=True)
    last_date = None

    for index, row in df.iterrows():
        if row['Allonge'] and row['Assis']:
            if last_date is None or row['formattedDate'] == last_date:
                streak += 1
            else:
                streak = 1
            last_date = row['formattedDate']
            if streak % 5 == 0 and lives < 2:
                lives += 1
        else:
            if lives > 0:
                lives -= 1
            else:
                streak = 0
                lives = 2

        results.append((row['SessionID'], streak, lives))
    
    return results

# Mise à jour avec les nouvelles séries et les valeurs des vies
results = calculate_daily_practice(df)
for index, streak, lives in results:
    df.at[index, 'serie'] = streak
    df.at[index, 'vies'] = lives

# Sauvegarder le DataFrame modifié
df.to_csv('../data/output.csv', index=False, quoting=1)
