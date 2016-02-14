import unittest

from fatools.core_ext.datetime import timedelta


class TimedeltaTests(unittest.TestCase):
    def test_timedelta_components(self):
        td = timedelta(seconds=129600)  # one and a half days
        self.assertSequenceEqual((0, 1, 12, 0, 0), td.components)
        self.assertEqual(td.components.weeks, 0)
        self.assertEqual(td.components.days, 1)
        self.assertEqual(td.components.hours, 12)
        self.assertEqual(td.components.minutes, 0)
        self.assertEqual(td.components.seconds, 0)

        td = timedelta(seconds=116640)  # 1.35 days
        self.assertSequenceEqual((0, 1, 8, 24, 0), td.components)

        td = timedelta(seconds=41472)  # 0.48 days
        self.assertSequenceEqual((0, 0, 11, 31, 12), td.components)

        td = timedelta(seconds=35)
        self.assertSequenceEqual((0, 0, 0, 0, 35), td.components)

    def test_timedelta_format_long(self):
        td = timedelta(seconds=129600)  # one and a half days
        self.assertEqual('1 day and 12 hours', td.format('long'))

    def test_timedelta_format_long_with_multiple_components(self):
        td = timedelta(seconds=116645)
        expected = '1 day, 8 hours, 24 minutes and 5 seconds'
        self.assertEqual(expected, td.format())

    def test_timedelta_format_short(self):
        td = timedelta(seconds=129600)  # one and a half days
        self.assertEqual('1d 12h', td.format('short'))

    def test_timedelta_format_short_with_multiple_components(self):
        td = timedelta(seconds=116645)  # one and a half days
        self.assertEqual('1d 8h', td.format('short'))

    def test_timedelta_format_with_limit(self):
        td = timedelta(seconds=116645)
        self.assertEqual('1 day and 8 hours', td.format(limit=2))

    def test_timedelta_format_zero(self):
        td = timedelta(seconds=0)
        self.assertEqual('0 seconds', td.format())
        self.assertEqual('0s', td.format('short'))

if __name__ == '__main__':
    unittest.main()
