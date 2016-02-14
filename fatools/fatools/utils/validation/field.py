class FieldInfo(object):
    __field__ = True

    def __init__(self, dtype=str, converter=None, choices=None, predicate=None,
                 default=None, **kwargs):
        super(FieldInfo, self).__init__()
        self.dtype = dtype
        self.converter = converter
        self.choices = choices
        self.predicate = predicate
        self.default = default
        self.meta = kwargs
