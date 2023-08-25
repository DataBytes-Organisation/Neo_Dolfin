from abc import ABC, abstractmethod

class IBasiqService(ABC):
    @abstractmethod
    def get_access_token(self):
        raise NotImplementedError

    @abstractmethod
    def get_all_transaction_data_for_user(self, access_token):
        raise NotImplementedError

    @abstractmethod
    def create_user_transaction_data_object(self, data, username, bucket_name, file_name):
        raise NotImplementedError

    @abstractmethod
    def get_headers(access_token):
        raise NotImplementedError