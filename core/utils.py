# coding: utf-8


from __future__ import absolute_import

try:
    import simplejson as json
except ImportError:
    import json


__all__ = ('json', 'raise_on')


def raise_on(condition, message='Condition failed'):
    if not condition:
        raise ValueError(message)
