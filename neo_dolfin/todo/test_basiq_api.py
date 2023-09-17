from services.basiq_service import BasiqService 
import pandas as pd

basiq_service = BasiqService()

def test_get_headers():
    '''
    Given a dummy access token, generate the expected headers for a basiq request
    '''

    headers = basiq_service.get_headers("ABCD1234")
    assert headers["authorization"] == "ABCD1234"

def test_get_access_token():
    access_token = basiq_service.get_access_token()
    assert access_token is not None


def test_get_transaction_data():
    access_token = basiq_service.get_access_token()
    transactions = basiq_service.get_all_transaction_data_for_user(access_token)
    Transactions = pd.json_normalize(transactions, record_path=['data'])
    df = pd.DataFrame(Transactions)
    assert len(df) == 500
