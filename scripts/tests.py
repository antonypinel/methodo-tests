import pytest
import pandas as pd
from datetime import datetime
from colorama import Fore, init
from update_csv import calculate_daily_practice

# Initialiser colorama
init(autoreset=True)

@pytest.fixture
def setup_dataframe():
    data = {
        "SessionID": [1] * 18,
        "Date": ["2023-07-01"] * 18,
        "Niveau": [1] * 18,
        "Allonge": [True, False] * 9,
        "Assis": [False, True] * 9,
        "serie": [0] * 18,
        "vies": [2] * 18
    }
    df = pd.DataFrame(data)
    df['formattedDate'] = pd.to_datetime(df['Date']).dt.date
    return df

# Tests
def test_double_level_1_completes_session(setup_dataframe):
    df = setup_dataframe
    results = calculate_daily_practice(df)
    assert results[0][1] == 1, "Deux exercices de niveau 1 doivent compléter une séance."

def test_single_level_2_completes_session(setup_dataframe):
    df = setup_dataframe
    df.loc[:, 'Niveau'] = 2
    results = calculate_daily_practice(df)
    assert results[0][1] == 1, "Un exercice de niveau 2 doit compléter une séance."

def test_non_completion_without_sufficient_exercises(setup_dataframe):
    df = setup_dataframe
    df.loc[:, 'Allonge'] = False
    df.loc[:, 'Assis'] = False
    results = calculate_daily_practice(df)
    assert all(res[1] == 0 for res in results), "Aucune pratique sans les exercices requis ne devrait compter."

def test_streak_increment_on_completion(setup_dataframe):
    df = setup_dataframe
    df.loc[:, 'Allonge'] = True
    df.loc[:, 'Assis'] = True
    results = calculate_daily_practice(df)
    assert results[-1][1] == 1, "La série devrait s'incrémenter après un jour de pratique complète."

def test_series_continuation_with_life_usage(setup_dataframe):
    df = setup_dataframe
    df.loc[5:6, 'Allonge'] = False
    df.loc[5:6, 'Assis'] = False
    results = calculate_daily_practice(df)
    assert results[6][1] == 1, "La série devrait continuer avec l'utilisation des vies."

def test_reset_series_without_lives(setup_dataframe):
    df = setup_dataframe
    df.loc[:, 'vies'] = 0
    results = calculate_daily_practice(df)
    assert all(res[1] == 0 for res in results), "La série devrait être réinitialisée sans vies disponibles."

def test_life_consumption_on_incomplete_practice(setup_dataframe):
    df = setup_dataframe
    df.loc[1:3, 'Allonge'] = False
    df.loc[1:3, 'Assis'] = False
    results = calculate_daily_practice(df)
    assert results[3][2] < 2, "Les vies devraient être consommées pour les jours sans pratique complète."

def test_life_gain_after_five_consecutive_days(setup_dataframe):
    df = setup_dataframe
    df.loc[:, 'Allonge'] = True
    df.loc[:, 'Assis'] = True
    results = calculate_daily_practice(df)
    assert results[4][2] == 2, "Une vie devrait être regagnée après 5 jours consécutifs de pratique."

def test_life_cap_at_two(setup_dataframe):
    df = setup_dataframe
    results = calculate_daily_practice(df)
    assert all(res[2] <= 2 for res in results), "Le nombre de vies ne devrait jamais dépasser 2."

def test_reset_lives_with_series_break(setup_dataframe):
    df = setup_dataframe
    df.loc[0:2, 'vies'] = 0
    df.loc[0:2, 'Allonge'] = False
    df.loc[0:2, 'Assis'] = False
    results = calculate_daily_practice(df)
    assert results[3][2] == 2, "Les vies devraient être réinitialisées à 2 après une rupture de série."

def test_correct_handling_of_malformatted_dates(setup_dataframe):
    df = setup_dataframe
    df.loc[:, 'Date'] = ['not a date'] * len(df)
    df['formattedDate'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
    results = calculate_daily_practice(df)
    assert all(pd.isna(date) for date in df['formattedDate']), "Les dates mal formatées devraient être gérées correctement."

def test_filtering_sessions_without_id(setup_dataframe):
    df = setup_dataframe
    df.loc[0, 'SessionID'] = None
    results = calculate_daily_practice(df[df['SessionID'].notna()])
    assert all(pd.notna(res[0]) for res in results), "Les sessions sans ID devraient être filtrées."

def test_multi_session_logic_in_single_day(setup_dataframe):
    df = setup_dataframe
    results = calculate_daily_practice(df)
    assert results[0][1] == 1, "Plusieurs séances en un seul jour devraient être combinées correctement."

def test_data_integrity_after_processing(setup_dataframe):
    df = setup_dataframe
    results = calculate_daily_practice(df)
    assert 'serie' in df.columns and 'vies' in df.columns, "Les données devraient contenir les colonnes 'serie' et 'vies' après traitement."

def test_handling_of_extreme_input_values(setup_dataframe):
    df = setup_dataframe
    df = pd.concat([df]*10)
    results = calculate_daily_practice(df)
    assert len(results) == len(df), "Le système devrait gérer correctement les entrées avec des valeurs extrêmes."

# Configuration pour colorama
def pytest_configure(config):
    config.addinivalue_line("markers", "colorama")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        print(Fore.RED + f"FAIL: {item.name}" + Fore.RESET)
    elif rep.when == "call" and rep.passed:
        print(Fore.GREEN + f"PASS: {item.name}" + Fore.RESET)