import abc
import os

from fatools.utils.schemable import FieldInfo, Schema
from fatools.utils.text import glued


# TODO add docstrings


class CmdOption(FieldInfo):
    def __init__(self, alias, *args, **kwargs):
        super(CmdOption, self).__init__(*args, **kwargs)
        self.alias = alias


class CpuHostOption(CmdOption):
    def __init__(self, alias, default=''):
        kwargs = dict(default=default)
        super(CpuHostOption, self).__init__(alias, **kwargs)

# ORIGINAL
# class CpuHostOption(CmdOption):
#     def __init__(self, alias, default='localhost'):
#         kwargs = dict(default=default)
#         super(CpuHostOption, self).__init__(alias, **kwargs)


class CpuOption(CmdOption):
    def __init__(self, alias, default=12):
        kwargs = dict(only_integer=True, greater_than=0, default=default)
        super(CpuOption, self).__init__(alias, **kwargs)


class Cmd(Schema):
    args = property(lambda self: self.cmdline.split())
    cmdline = property(lambda self: self.build())

    def __str__(self):
        return self.build()

    @abc.abstractproperty
    def jobname(self):
        return NotImplemented

    def build(self, **kwargs):
        opts = [self.program]
        for name in self._sorted_fields():
            option = self._format_option(
                name, self._fields[name].alias, getattr(self, name))
            if option is not None:
                # if 'host' in option:
                #    opt_host = option.split(':')
                #    opt_host = [element.strip() for element in opt_host]
                #    option = ':'.join(opt_host)
                opts.append(option)
        return glued(opts, ' ')

    def _format_option(self, name, alias, value):
        if value is None or value is False:
            return None
        elif value is True:  # flag-like option (e.g., --verbose)
            return alias
        value = self._format_option_value(name, value)
        if value is None:
            return None
        return '{} {}'.format(alias, value)

    def _format_option_value(self, name, value):
        return str(value)

    def _sorted_fields(self):
        return sorted(self._fields, key=lambda f: self._fields[f].alias)


class CmdWithInputFiles(Cmd):
    def __init__(self, *files, **kwargs):
        self.input_files = files
        super(CmdWithInputFiles, self).__init__(**kwargs)

    @property
    def filenames(self):
        return tuple(os.path.basename(f) for f in self.input_files)

    def build(self, *files, **kwargs):
        cmdline = super(CmdWithInputFiles, self).build(**kwargs)
        input_files = files if files else self.input_files
        return glued(tuple([cmdline]) + input_files, ' ')
