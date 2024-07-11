import pandas as pd
from datetime import timedelta
from colorama import Fore, Style

# Charger le script principal
def correct_formatted_date(df):
    df['Date'] = pd.to_datetime(df['Date'], unit='s')
    df['formattedDate'] = df['Date'].dt.strftime('%d/%m/%Y')
    return df

def is_valid_practice(group):
    level_1_count = len(group[group['Niveau'] == 1])
    level_2_count = len(group[group['Niveau'] == 2])
    return (level_2_count >= 1) or (level_1_count >= 2)

def calculate_streaks_and_lives(df):
    df['Streak'] = 0
    df['Lives'] = 2
    session_ids = df['SessionID'].unique()

    for session_id in session_ids:
        session_data = df[df['SessionID'] == session_id]
        streak = 0
        lives = 2
        last_date = None

        for i in session_data.index:
            current_date = df.loc[i, 'Date'].date()
            current_group = session_data[session_data['Date'].dt.date == current_date]

            if last_date is None or current_date != last_date:
                # Handling missed days
                if last_date is not None and (current_date - last_date).days > 1:
                    days_missed = (current_date - last_date).days - 1
                    lives -= days_missed
                    if lives < 0:
                        streak = 0
                        lives = 2

                # Valid practice check
                if is_valid_practice(current_group):
                    streak += 1
                    if streak % 5 == 0:
                        lives += 1
                    if lives > 2:
                        lives = 2
                else:
                    streak = 0  # Reset streak for invalid practice
                    lives -= 1
                    if lives < 0:
                        streak = 0
                        lives = 2

            # Ensure only the first practice of the day is counted
            if last_date == current_date:
                df.at[i, 'Streak'] = streak
                df.at[i, 'Lives'] = lives
                continue

            df.at[i, 'Streak'] = streak
            df.at[i, 'Lives'] = lives

            last_date = current_date
    return df

def cast_niveau(df):
    df['Niveau'] = df['Niveau'].apply(lambda x: int(float(x)) if pd.notnull(x) else x)
    return df

# Charger les données
data = pd.read_csv('data/input.csv')

# Correction du format de la colonne 'formattedDate'
data = correct_formatted_date(data)
data = cast_niveau(data)

# Fonction pour exécuter les tests
def run_tests():
    def check(condition, test_name, error_message=""):
        if condition:
            print(Fore.GREEN + f"{test_name}: OK" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"{test_name}: KO" + Style.RESET_ALL)
            if error_message:
                print(Fore.RED + error_message + Style.RESET_ALL)

    # Test 1 : Vérifier la pratique valide
    group = pd.DataFrame({
        'Niveau': [1, 1, 2, 2],
        'Allonge': [True, True, True, True],
        'Assis': [True, True, True, True]
    })
    check(is_valid_practice(group) == True, "Test 1")

    # Test 2 : Vérifier la pratique invalide
    group = pd.DataFrame({
        'Niveau': [1, 1],
        'Allonge': [True, True],
        'Assis': [True, True]
    })
    check(is_valid_practice(group) == True, "Test 2.1")

    group = pd.DataFrame({
        'Niveau': [1],
        'Allonge': [True],
        'Assis': [False]
    })
    check(is_valid_practice(group) == False, "Test 2.2")

    # Préparation des DataFrames de tests et des résultats attendus
    data = pd.DataFrame({
        'Date': [1618937885, 1618937885, 1618937885, 1618937885, 1618941909, 1618941909, 1618990359, 1618996829],
        'Niveau': [2, 2, 2, 2, 2, 2, 2, 2],
        'Allonge': [True, True, True, True, True, True, True, True],
        'Assis': [True, False, True, True, True, False, False, False],
        'SessionID': [
            'ed73e2a7-8f8a-493c-9388-c7cc4714b0ad', 
            'ed73e2a7-8f8a-493c-9388-c7cc4714b0ad', 
            'ed73e2a7-8f8a-493c-9388-c7cc4714b0ad', 
            'ed73e2a7-8f8a-493c-9388-c7cc4714b0ad', 
            'fd305c40-0331-4bc3-a23b-aac2626fdfa2', 
            'fd305c40-0331-4bc3-aac2626fdfa2', 
            'ed73e2a7-8f8a-493c-9388-c7cc4714b0ad', 
            '1e481168-243e-4e64-87d3-a2b5085a77a2'
        ],
        'formattedDate': [
            '20/04/2021', '20/04/2021', '20/04/2021', '20/04/2021',
            '20/04/2021', '20/04/2021', '21/04/2021', '21/04/2021'
        ],
        'Streak': [0]*8,
        'Lives': [2]*8
    })

    data['Date'] = pd.to_datetime(data['Date'], unit='s')

    # Test 3 : Vérifier la régénération des vies après cinq jours de pratique
    df = data.copy()
    for _ in range(4):
        new_row = data.iloc[0].copy()
        new_row['Date'] = new_row['Date'] + timedelta(days=1)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df = calculate_streaks_and_lives(df)
    check(df['Lives'].iloc[-1] == 2, "Test 3", f"Expected Lives: 2, Found: {df['Lives'].iloc[-1]}")

    # Test 4 : Vérifier le nombre maximum de vies
    df = data.copy()
    for _ in range(10):
        new_row = data.iloc[0].copy()
        new_row['Date'] = new_row['Date'] + timedelta(days=1)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df = calculate_streaks_and_lives(df)
    check(df['Lives'].iloc[-1] == 2, "Test 4", f"Expected Lives: 2, Found: {df['Lives'].iloc[-1]}")

    # Test 5 : Vérifier que les streaks continuent avec des pratiques valides
    df = data.copy()
    df = calculate_streaks_and_lives(df)
    check(df['Streak'].iloc[0] == 1, "Test 5.1", f"Expected Streak: 1, Found: {df['Streak'].iloc[0]}")
    check(df['Streak'].iloc[-1] == 1, "Test 5.2", f"Expected Streak: 1, Found: {df['Streak'].iloc[-1]}")

    # Test 6 : Vérifier la réinitialisation des streaks en cas de pratique invalide
    df = data.copy()
    new_row = data.iloc[0].copy()
    new_row['Date'] = new_row['Date'] + timedelta(days=1)
    new_row['Niveau'] = 0
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df = calculate_streaks_and_lives(df)
    check(df['Streak'].iloc[-1] == 0, "Test 6", f"Expected Streak: 0, Found: {df['Streak'].iloc[-1]}")

    # Test 7 : Vérifier que plusieurs pratiques valides le même jour sont comptées comme une seule pratique
    df = data.copy()
    new_row = data.iloc[0].copy()
    new_row['Date'] = new_row['Date']
    new_row['Niveau'] = 2
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df = calculate_streaks_and_lives(df)
    check(df['Streak'].iloc[0] == 1, "Test 7", f"Expected Streak: 1, Found: {df['Streak'].iloc[0]}")

    # Test 8 : Vérifier les vies après des jours manqués
    df = data.copy()
    df.loc[df.index[-1], 'Date'] = df.loc[df.index[0], 'Date'] + timedelta(days=10)
    df = calculate_streaks_and_lives(df)
    check(df['Lives'].iloc[-1] == 2, "Test 8", f"Expected Lives: 2, Found: {df['Lives'].iloc[-1]}")

    # Test 9 : Vérifier les streaks après des jours manqués
    df = data.copy()
    df.loc[df.index[-1], 'Date'] = df.loc[df.index[0], 'Date'] + timedelta(days=10)
    df = calculate_streaks_and_lives(df)
    check(df['Streak'].iloc[-1] == 1, "Test 9", f"Expected Streak: 1, Found: {df['Streak'].iloc[-1]}")

    # Test 10 : Vérifier l'incrémentation des streaks avec des pratiques valides
    df = data.copy()
    for _ in range(2):
        new_row = data.iloc[0].copy()
        new_row['Date'] = new_row['Date'] + timedelta(days=1)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df = calculate_streaks_and_lives(df)
    check(df['Streak'].iloc[-1] == 2, "Test 10", f"Expected Streak: 2, Found: {df['Streak'].iloc[-1]}")

    # Test 11 : Vérifier la pratique valide avec des niveaux mixtes
    group = pd.DataFrame({
        'Niveau': [1, 2],
        'Allonge': [True, True],
        'Assis': [True, True]
    })
    check(is_valid_practice(group) == True, "Test 11")

    # Test 12 : Vérifier la pratique invalide avec un nombre insuffisant d'exercices de niveau 1
    group = pd.DataFrame({
        'Niveau': [1],
        'Allonge': [True],
        'Assis': [True]
    })
    check(is_valid_practice(group) == False, "Test 12")

    # Test 13 : Vérifier le maintien des streaks avec des pratiques valides continues
    df = data.copy()
    for _ in range(5):
        new_row = data.iloc[0].copy()
        new_row['Date'] = new_row['Date'] + timedelta(days=1)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df = calculate_streaks_and_lives(df)
    check(df['Streak'].iloc[-1] == 5, "Test 13", f"Expected Streak: 5, Found: {df['Streak'].iloc[-1]}")

    # Test 14 : Vérifier la réinitialisation des vies après la perte de toutes les vies
    df = data.copy()
    for _ in range(3):
        new_row = data.iloc[0].copy()
        new_row['Date'] = new_row['Date'] + timedelta(days=2)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df = calculate_streaks_and_lives(df)
    check(df['Lives'].iloc[-1] == 2, "Test 14.1", f"Expected Lives: 2, Found: {df['Lives'].iloc[-1]}")
    check(df['Streak'].iloc[-1] == 0, "Test 14.2", f"Expected Streak: 0, Found: {df['Streak'].iloc[-1]}")

    print("All tests completed.")

if __name__ == "__main__":
    run_tests()
