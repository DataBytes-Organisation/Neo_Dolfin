from abc import ABC, abstractmethod

class IS3Service(ABC):
    @abstractmethod
    def set_object(self, bucket_name, object_name, object_bytes):
        raise NotImplementedError

    @abstractmethod
    def get_specified_object(bucket_name, object_name):
        raise NotImplementedError

    @abstractmethod
    def get_latest_object(bucket_name, username):
        raise NotImplementedError

    @abstractmethod
    def create_bucket(bucket_name, configuration_json = None):
        raise NotImplementedError

    @abstractmethod
    def delete_bucket(bucket_name):
        raise NotImplementedError