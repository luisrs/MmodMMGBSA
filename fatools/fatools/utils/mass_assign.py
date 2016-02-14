from fatools.utils.kernel import getattrnames, getclassname
from fatools.utils.text import glued


class MassAssignmentError(Exception):
    """Raised when mass-assigning a guarded attribute."""
    def __init__(self, classinfo, attr_name):
        self.classinfo = classinfo
        self.attr_name = attr_name

    def __str__(self):
        return ("cannot mass-assign protected attribute for {}: '{}'"
                .format(self.classinfo.__name__, self.attr_name))


class MassAssignable(object):
    """Abstract class that enables mass-assignment when creating instances.

    Mass-assignment allows to pass instance attributes during initialization
    as keyword arguments into the constructor::

        >>> ma = MassAssignable(attr1='val1', attr2='val2', ...)
        >>> ma.attr1
        'val1'
        >>> ma.attr2
        'val2'
        ...

    This is very convenient for creating instances of dynamic classes whose
    attributes are not pre-defined at the class declaration stage.

    Concrete classes may restrict which attributes can be mass-assigned
    by overriding :attr:`assignable_attributes` and :attr:`guarded_attributes`
    class variables.
    Attributes that are not contained in the former will be ignored when
    mass-assigned, while an :exc:`MassAssignmentError` error will be raised for
    those (guarded) attributes that are declared in the latter.
    The wildcard ``'*'`` can be used to accept any attribute (default value for
    :attr:`assignable_attributes` class variable).

    Examples
    --------
    >>> from fatools.utils.kernel import MassAssignable
    >>> class Config(MassAssignable):
    ...     assignable_attributes = ('cpu', 'host')
    ...     guarded_attributes = ('cmd',)
    ...
    >>> cfg = Config(cpu=8, host='localhost', tpp=4)
    >>> cfg
    Config(cpu=8, host='localhost')
    >>> cfg.cpu
    8
    >>> cfg.host
    'localhost'
    >>> Config(cpu=8, host='localhost', cmd='program')
    Traceback (most recent call last):
      ...
    fatools.utils.kernel.MassAssignmentError: cannot mass-assign protected \
attribute for Config: 'cmd'

    """

    assignable_attributes = ('*',)
    guarded_attributes = ()

    def __init__(self, **kwargs):
        super(MassAssignable, self).__init__()
        self._assign_attributes(kwargs)

    @classmethod
    def can_assign_attribute(cls, attr_name):
        return (cls.assignable_attributes
                and cls.assignable_attributes[0] == '*') \
            or attr_name in cls.assignable_attributes

    @classmethod
    def is_attribute_guarded(cls, attr_name):
        return (cls.guarded_attributes and cls.guarded_attributes[0] == '*') \
            or attr_name in cls.guarded_attributes

    def __repr__(self):
        converter = lambda key: '{}={}'.format(key, repr(getattr(self, key)))
        attr_repr = glued(sorted(getattrnames(self)), ', ', converter)
        return '{}({})'.format(getclassname(self), attr_repr)

    def _assign_attributes(self, attributes):
        for name in attributes.keys():
            if self.__class__.is_attribute_guarded(name):
                raise MassAssignmentError(self.__class__, name)
            elif self.__class__.can_assign_attribute(name):
                setattr(self, name, attributes[name])
