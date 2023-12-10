import API_db_op


def test_unit_0():
    print(API_db_op.init_dolfin_db())


def test_unit_1():
    print(API_db_op.register_user('databytes@gmail.com', '61479018001', 'Wentworth', '', '', '12345'))
    print(API_db_op.register_user('databytes@gmail.com', '61479018001', 'Whistler', '', '', '12345'))
    print(API_db_op.register_user('databytes@gmail.com', '61479018001', 'Gilfoyle', '', '', '12345'))
    print(API_db_op.register_user('databytes@gmail.com', '61479018001', 'gavinBelson', '', '', '12345'))
    print(API_db_op.register_user('databytes@gmail.com', '61479018001', 'richard', '', '', '12345'))


def test_unit_2():
    print(API_db_op.register_basiq_id(1))
    print(API_db_op.register_basiq_id(2))
    print(API_db_op.register_basiq_id(3))
    print(API_db_op.register_basiq_id(4))
    print(API_db_op.register_basiq_id(5))


def test_unit_3():
    print(API_db_op.link_bank_account(1))
    print(API_db_op.link_bank_account(2))
    print(API_db_op.link_bank_account(3))
    print(API_db_op.link_bank_account(4))
    print(API_db_op.link_bank_account(5))


def test_unit_4():
    print(API_db_op.cache_transactions(1, API_db_op.request_transactions(1)))
    print(API_db_op.cache_transactions(2, API_db_op.request_transactions(2)))
    print(API_db_op.cache_transactions(3, API_db_op.request_transactions(3)))
    print(API_db_op.cache_transactions(4, API_db_op.request_transactions(4)))
    print(API_db_op.cache_transactions(5, API_db_op.request_transactions(5)))

def test_unit_5():
    print(API_db_op.fetch_transactions_by_user(1))