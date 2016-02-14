import unittest
from fatools.utils.inflection import underscore
from fatools.utils.kernel import getattrnames, MissingArgumentError
from fatools.utils.schemable import FieldInfo, Schema, Schemable
from fatools.utils.validation import ValidationError

ip_address_format = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'


class Config(Schema):
    host = FieldInfo(format=ip_address_format, default='127.0.0.1')
    cpu = FieldInfo(only_integer=True, ge=1, default=1)
    user = FieldInfo(type=(str, int), converter=underscore)
    pwd = FieldInfo(type=str, predicate=lambda pwd: len(pwd) < 20)
    env = FieldInfo(allow_none=True)

    def _after_initialize(self):
        self._initialized = True


class SchemableTests(unittest.TestCase):
    def test_create_empty_schema(self):
        class EmptySchema:
            __metaclass__ = Schemable
        self.assertRaisesRegexp(TypeError, 'cannot instantiate', EmptySchema)

    def test_get_fields(self):
        self.assertEqual(
            ['cpu', 'env', 'host', 'pwd', 'user'],
            sorted(Config._fields))


class SchemaTests(unittest.TestCase):
    def test_attribute_conversion(self):
        cfg = Config(user='UserName', pwd='123456')
        self.assertEqual('user_name', cfg.user)

    def test_callback_after_initialize(self):
        cfg = Config(user='UserName', pwd='123456')
        self.assertTrue(cfg._initialized)

    def test_create_schema(self):
        cfg = Config(host='192.168.0.1', cpu=2, user='username', pwd='123456')
        self.assertEqual('192.168.0.1', cfg.host)
        self.assertEqual(2, cfg.cpu)
        self.assertEqual('username', cfg.user)
        self.assertEqual('123456', cfg.pwd)

    def test_create_schema_without_required_attribute(self):
        with self.assertRaises(MissingArgumentError) as err:
            Config(cpu=8)
        expected_err = "Config() missing 2 required fields: 'pwd' and 'user'"
        self.assertEqual(expected_err, str(err.exception))

    def test_create_schema_with_defaults(self):
        cfg = Config(user='username', pwd='123456')
        self.assertEqual('127.0.0.1', cfg.host)
        self.assertEqual(1, cfg.cpu)
        self.assertEqual('username', cfg.user)
        self.assertEqual('123456', cfg.pwd)

    def test_create_schema_with_invalid_attribute(self):
        with self.assertRaises(ValidationError) as err:
            Config(user=[], pwd='123456')
        expected_err = "invalid value for 'user', expected str or int type, " \
                       "got [] (list)"
        self.assertEqual(expected_err, str(err.exception))

        with self.assertRaises(ValidationError) as err:
            Config(user='username', pwd='12345678901234567890123456789')
        expected_err = "invalid value for field 'pwd', " \
                       "got '12345678901234567890123456789'"
        self.assertEqual(expected_err, str(err.exception))

        with self.assertRaises(ValidationError) as err:
            Config(user='username', pwd='123456', cpu=0)
        expected_err = "'cpu' is less than 1"
        self.assertEqual(expected_err, str(err.exception))

    def test_create_schema_with_non_assignable_attributes(self):
        cfg = Config(id=169, user='username', pwd='123456', role=9)
        self.assertEqual('username', cfg.user)
        self.assertEqual('123456', cfg.pwd)
        self.assertRaises(AttributeError, getattr, cfg, 'id')
        self.assertRaises(AttributeError, getattr, cfg, 'role')

    def test_create_with_nullable_attributes(self):
        cfg = Config(user='username', pwd='123456')
        self.assertIsNone(cfg.env)

if __name__ == '__main__':
    unittest.main()
