import unittest
from fatools.utils.caching import cached_property


class CachedPropertyTests(unittest.TestCase):
    def test_cached_property(self):
        constant = []

        class C(object):
            access_count = 0

            @cached_property
            def calculated_property(self):
                self.access_count += 1
                return constant

        c = C()
        self.assertEqual(cached_property, C.calculated_property.__class__)
        self.assertIs(c.calculated_property, constant)
        self.assertEqual(1, c.access_count)

        self.assertIs(c.calculated_property, constant)
        self.assertIs(c.calculated_property, constant)
        self.assertEqual(1, c.access_count)

    def test_cached_property_with_alias(self):
        class C(object):
            access_count = 0

            def get_absolute_url(self):
                self.access_count += 1
                return 'https://github.com/franciscoadasme'
            url = cached_property(get_absolute_url, name='url')

        c = C()
        self.assertEqual('https://github.com/franciscoadasme', c.url)
        self.assertEqual('https://github.com/franciscoadasme', c.url)
        self.assertEqual('https://github.com/franciscoadasme', c.url)
        self.assertEqual(1, c.access_count)
