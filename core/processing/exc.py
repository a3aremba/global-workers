# coding: utf-8


__all__ = ('ProcessingException', 'UnknownProcessingTypeException')


class ProcessingException(Exception):
    pass


class UnknownProcessingTypeException(ProcessingException):
    pass


class ProcessingRetryLimitException(ProcessingException):
    def __init__(self, retry):
        """
        :param retry: seconds
        """
        self.retry = retry


class ProcessingDelayedException(ProcessingException):
    pass
