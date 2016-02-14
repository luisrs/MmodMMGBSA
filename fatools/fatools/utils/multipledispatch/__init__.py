"""A relatively sane approach to multiple dispatch in Python.

This implementation of multiple dispatch is efficient, mostly complete,
performs static analysis to avoid conflicts, and provides optional
namespace support. It looks good too.

Taken from https://github.com/mrocklin/multipledispatch at Aug 8, 2015.

"""

from fatools.utils.multipledispatch.core import dispatch
from fatools.utils.multipledispatch.dispatcher import (
    Dispatcher, halt_ordering, restart_ordering, MDNotImplementedError)

__version__ = '0.4.8'
