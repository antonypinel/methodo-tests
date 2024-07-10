import pytest
import pandas as pd
from update_csv import calculate_series_and_lives

# Fonction d'aide pour exécuter les tests
def run_test(data, expected_results):
    df = pd.DataFrame(data)
    result_df = calculate_series_and_lives(df)
    for i, expected in enumerate(expected_results):
        for key, value in expected.items():
            assert result_df.at[i, key] == value, f"Failed on row {i}, column {key}. Expected {value}, got {result_df.at[i, key]}"

# Tests individuels
def test_initial_conditions():
    run_test(
        [{'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '01/07/2024'}],
        [{'serie': 1, 'lives': 2}]
    )

def test_consecutive_days():
    run_test(
        [
            {'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '01/07/2024'},
            {'Date': '2024-07-02', 'Niveau': 1, 'Allonge': False, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '02/07/2024'}
        ],
        [{'serie': 1, 'lives': 2}, {'serie': 2, 'lives': 2}]
    )

def test_gap_in_practice():
    run_test(
        [
            {'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '01/07/2024'},
            {'Date': '2024-07-03', 'Niveau': 1, 'Allonge': False, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '03/07/2024'}
        ],
        [{'serie': 1, 'lives': 2}, {'serie': 0, 'lives': 1}]
    )

def test_life_loss_and_recovery():
    run_test(
        [
            {'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '01/07/2024'},
            {'Date': '2024-07-02', 'Niveau': 1, 'Allonge': False, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '02/07/2024'},
            {'Date': '2024-07-04', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '04/07/2024'}
        ],
        [{'serie': 1, 'lives': 2}, {'serie': 2, 'lives': 2}, {'serie': 0, 'lives': 1}]
    )

def test_life_recharge():
    run_test(
        [
            {'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '01/07/2024'},
            {'Date': '2024-07-02', 'Niveau': 1, 'Allonge': False, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '02/07/2024'},
            {'Date': '2024-07-03', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '03/07/2024'},
            {'Date': '2024-07-04', 'Niveau': 1, 'Allonge': False, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '04/07/2024'},
            {'Date': '2024-07-05', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '05/07/2024'},
            {'Date': '2024-07-06', 'Niveau': 1, 'Allonge': False, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '06/07/2024'}
        ],
        [{'serie': 1, 'lives': 2}, {'serie': 2, 'lives': 2}, {'serie': 3, 'lives': 2}, {'serie': 4, 'lives': 2}, {'serie': 5, 'lives': 2}, {'serie': 6, 'lives': 2}]
    )

def test_series_reset_after_life_exhaustion():
    run_test(
        [
            {'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '01/07/2024'},
            {'Date': '2024-07-02', 'Niveau': 1, 'Allonge': False, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '02/07/2024'},
            {'Date': '2024-07-05', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '05/07/2024'}
        ],
        [{'serie': 1, 'lives': 2}, {'serie': 2, 'lives': 2}, {'serie': 0, 'lives': 1}]
    )

def test_multiple_users():
    run_test(
        [
            {'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '01/07/2024'},
            {'Date': '2024-07-02', 'Niveau': 1, 'Allonge': False, 'Assis': True, 'SessionID': 'user2', 'formattedDate': '02/07/2024'}
        ],
        [{'serie': 1, 'lives': 2}, {'serie': 1, 'lives': 2}]
    )

def test_long_series():
    run_test(
        [
            {'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '01/07/2024'},
            {'Date': '2024-07-02', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '02/07/2024'},
            {'Date': '2024-07-03', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '03/07/2024'},
            {'Date': '2024-07-04', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '04/07/2024'},
            {'Date': '2024-07-05', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '05/07/2024'},
            {'Date': '2024-07-06', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '06/07/2024'}
        ],
        [{'serie': 1, 'lives': 2}, {'serie': 2, 'lives': 2}, {'serie': 3, 'lives': 2}, {'serie': 4, 'lives': 2}, {'serie': 5, 'lives': 2}, {'serie': 6, 'lives': 2}]
    )

def test_interrupted_series_with_life_loss():
    run_test(
        [
            {'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '01/07/2024'},
            {'Date': '2024-07-02', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '02/07/2024'},
            {'Date': '2024-07-04', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '04/07/2024'},
            {'Date': '2024-07-05', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '05/07/2024'}
        ],
        [{'serie': 1, 'lives': 2}, {'serie': 2, 'lives': 2}, {'serie': 0, 'lives': 1}, {'serie': 1, 'lives': 1}]
    )

def test_life_exhaustion():
    run_test(
        [
            {'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '01/07/2024'},
            {'Date': '2024-07-03', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '03/07/2024'},
            {'Date': '2024-07-05', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '05/07/2024'},
            {'Date': '2024-07-07', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '07/07/2024'}
        ],
        [{'serie': 1, 'lives': 2}, {'serie': 0, 'lives': 1}, {'serie': 0, 'lives': 0}, {'serie': 0, 'lives': 0}]
    )

def test_life_recharge_with_extended_series():
    run_test(
        [
            {'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '01/07/2024'},
            {'Date': '2024-07-02', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '02/07/2024'},
            {'Date': '2024-07-03', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '03/07/2024'},
            {'Date': '2024-07-04', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '04/07/2024'},
            {'Date': '2024-07-05', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '05/07/2024'},
            {'Date': '2024-07-06', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '06/07/2024'},
            {'Date': '2024-07-07', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '07/07/2024'}
        ],
        [{'serie': 1, 'lives': 2}, {'serie': 2, 'lives': 2}, {'serie': 3, 'lives': 2}, {'serie': 4, 'lives': 2}, {'serie': 5, 'lives': 2}, {'serie': 6, 'lives': 2}, {'serie': 7, 'lives': 2}]
    )

def test_life_exhaustion_and_series_reset():
    run_test(
        [
            {'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '01/07/2024'},
            {'Date': '2024-07-03', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '03/07/2024'},
            {'Date': '2024-07-05', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '05/07/2024'},
            {'Date': '2024-07-09', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '09/07/2024'}
        ],
        [{'serie': 1, 'lives': 2}, {'serie': 0, 'lives': 1}, {'serie': 0, 'lives': 0}, {'serie': 0, 'lives': 0}]
    )

def test_multiple_users_with_series():
    run_test(
        [
            {'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': False, 'SessionID': 'user1', 'formattedDate': '01/07/2024'},
            {'Date': '2024-07-02', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user1', 'formattedDate': '02/07/2024'},
            {'Date': '2024-07-01', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user2', 'formattedDate': '01/07/2024'},
            {'Date': '2024-07-02', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user2', 'formattedDate': '02/07/2024'},
            {'Date': '2024-07-03', 'Niveau': 1, 'Allonge': True, 'Assis': True, 'SessionID': 'user2', 'formattedDate': '03/07/2024'}
        ],
        [{'serie': 1, 'lives': 2}, {'serie': 2, 'lives': 2}, {'serie': 1, 'lives': 2}, {'serie': 2, 'lives': 2}, {'serie': 3, 'lives': 2}]
    )

if __name__ == "__main__":
    pytest.main()
