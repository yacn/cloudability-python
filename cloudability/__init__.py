"""Python Cloudability API Wrapper"""

__version__ = '0.1.0'
__all__ = ['Cloudability']

USER_AGENT = 'Cloudability Python API Wrapper %s' % __version__

from cloudability.client import Cloudability
