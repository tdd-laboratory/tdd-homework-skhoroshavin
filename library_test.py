import unittest
import library

NUM_CORPUS = '''
On the 5th of May every year, Mexicans celebrate Cinco de Mayo. This tradition
began in 1845 (the twenty-second anniversary of the Mexican Revolution), and
is the 1st example of a national independence holiday becoming popular in the
Western Hemisphere. (The Fourth of July didn't see regular celebration in the
US until 15-20 years later.) It is celebrated by 77.9% of the population--
trending toward 80.
'''

class TestCase(unittest.TestCase):

    # Helper function
    def extract_data(self, text, extractors):
        return [x[1].group(0) for x in library.scan(text, extractors)]

    def assert_extract(self, text, extractors, *expected):
        actual = self.extract_data(text, extractors)
        self.assertEqual(str(actual), str([x for x in expected]))

    # First unit test; prove that if we scan NUM_CORPUS looking for mixed_ordinals,
    # we find "5th" and "1st".
    def test_mixed_ordinals(self):
        self.assert_extract(NUM_CORPUS, library.mixed_ordinals, '5th', '1st')

    # Second unit test; prove that if we look for integers, we find four of them.
    def test_integers(self):
        self.assert_extract(NUM_CORPUS, library.integers, '1845', '15', '20', '80')

    # Third unit test; prove that if we look for integers where there are none, we get no results.
    def test_no_integers(self):
        self.assert_extract("no integers", library.integers)

    # 4. Prove that if we look for iso8601 dates we find some of them
    def test_dates_iso8601(self):
        self.assert_extract('I was born on 2015-07-25.', library.dates_iso8601, '2015-07-25')

    # 5. Prove that we don't match dates with impossible day
    def test_dates_iso8601_dont_match_too_big_day(self):
        self.assert_extract('There is no such date as 2015-07-32.', library.dates_iso8601)

    # 6. Prove that we don't match dates with impossible month
    def test_dates_iso8601_dont_match_too_big_month(self):
        self.assert_extract('There is no such date as 2015-13-25.', library.dates_iso8601)

    # 7. Prove that if we look for dates in fmt2 we find some of them
    def test_dates_fmt2(self):
        self.assert_extract('I was born on 25 Jan 2017.', library.dates_fmt2, '25 Jan 2017')

    # A bunch of tests as required by Step 11

    # In fact when considering all combinations from requirement on iso8601 dates there should be
    # 3*2*3 = 18 tests just for happy path, and a lot more for unhappy ones. I'll omit most of them
    # so that I'll have time to demonstrate most interesting ones. In fact one of main points of TDD
    # is to start fixing tests right after they fail and avoid writing tests that pass. That way
    # problems can be "triangulated" with much less number of tests.
    def test_dates_iso8601_match_dates_with_millisecond_accurate_timestamps(self):
        self.assert_extract('Database crash happened at 2018-06-22 18:22:19.123.', library.dates_iso8601, '2018-06-22 18:22:19.123')

    def test_dates_iso8601_match_dates_with_second_accurate_timestamps(self):
        self.assert_extract('Database crash happened at 2018-06-22 18:22:19.', library.dates_iso8601, '2018-06-22 18:22:19')

    def test_dates_iso8601_match_dates_with_minute_accurate_timestamps(self):
        self.assert_extract('At 2018-06-22 18:22 ops were very unhappy.', library.dates_iso8601, '2018-06-22 18:22')

    def test_dates_iso8601_match_dates_with_second_accurate_timestamps_and_t_delimiter(self):
        self.assert_extract('Database crash happened at 2018-06-22T18:22:19.', library.dates_iso8601, '2018-06-22T18:22:19')

    def test_dates_iso8601_match_dates_with_second_accurate_timestamps_and_3_letter_timezone(self):
        self.assert_extract('Database crash happened at 2018-06-22 18:22:19MDT.', library.dates_iso8601, '2018-06-22 18:22:19MDT')

    def test_dates_iso8601_match_dates_with_second_accurate_timestamps_and_1_letter_timezone(self):
        self.assert_extract('Database crash happened at 2018-06-22 18:22:19Z.', library.dates_iso8601, '2018-06-22 18:22:19Z')

    def test_dates_iso8601_match_dates_with_second_accurate_timestamps_and_offset_timezone(self):
        self.assert_extract('Database crash happened at 2018-06-22 18:22:19+0300.', library.dates_iso8601, '2018-06-22 18:22:19+0300')

    # Some unhappy examples - still for iso8601 dates.
    def test_dates_iso8601_dont_match_dates_with_second_accurate_timestamps_and_offset_timezone_when_hour_is_invalid(self):
        self.assert_extract('Database crash happened at 2018-06-22 25:22:19+0300.', library.dates_iso8601)

    def test_dates_iso8601_dont_match_dates_with_second_accurate_timestamps_and_offset_timezone_when_timezone_is_invalid(self):
        self.assert_extract('Database crash happened at 2018-06-22 18:22:19+2600.', library.dates_iso8601)

    # Some more tests for date fmt2, both positive and negative. There could be lots of them as well
    def test_dates_fmt2_match_dates_with_comma_after_month(self):
        self.assert_extract('I was born on 25 Jan, 2017.', library.dates_fmt2, '25 Jan, 2017')

    def test_dates_fmt2_dont_match_dates_with_incorrect_day(self):
        self.assert_extract('I was born on 33 Jan 2017.', library.dates_fmt2)

    def test_dates_fmt2_dont_match_dates_with_extra_space_before_month(self):
        self.assert_extract('I was born on 25  Jan 2017.', library.dates_fmt2)

    # Now on to number extraction When you're extracting numbers, you should support comma-separated groupings, as in "123,456,789".
    def test_numbers_support_comma_separated_groupings(self):
        self.assert_extract('We''ve got 123,456,789 issues on our tracker, that''s awful.', library.dates_fmt2, '123,456,789')

    def test_numbers_support_comma_separated_groupings_with_first_group_shorter_than_3(self):
        self.assert_extract('We''ve got just 1,234,567 issues on our tracker, what a relief.', library.dates_fmt2, '1,234,567')

    def test_numbers_dont_match_comma_separated_groupings_last_group_shorter_than_3(self):
        self.assert_extract('We''ve got just 1,234,56 issues on our tracker.', library.dates_fmt2)

    # And now back on to tests that show deficiencies in current implementation even without extra requirements from Alice
    def test_dates_iso8601_dont_match_zero_day(self):
        self.assert_extract('There is no such date as 2015-07-00.', library.dates_iso8601)

    def test_dates_iso8601_dont_match_zero_month(self):
        self.assert_extract('There is no such date as 2015-00-25.', library.dates_iso8601)

    def test_dates_iso8601_dont_match_impossible_date(self):
        self.assert_extract('There is no such date as 2015-06-31.', library.dates_iso8601)

    def test_dates_iso8601_dont_match_date_that_can_be_possible_in_leap_year(self):
        self.assert_extract('There is no such date as 2015-02-29.', library.dates_iso8601)

    def test_dates_iso8601_match_possible_date_in_leap_year(self):
        self.assert_extract('I was born on 2016-02-29.', library.dates_iso8601, '2016-02-29')

    def test_dates_iso8601_match_date_in_the_end_of_string(self):
        self.assert_extract('I was born on 2016-02-29', library.dates_iso8601, '2016-02-29')

    # Bonus! In fact I'm a big fan of yet another approach to tests, which is called property based testing.
    # I've mentioned that a couple of times, but now I see a chance to give a hint at it's power.
    # Main idea is to just come up with some properties (and there are already some patterns exist to help find
    # such properties), possibly write generator function to create valid examples and then throw hundreds
    # of examples at test. There are multiple frameworks for doing this in different languages, an excellent
    # example of such framework for Python is Hypothesis. It already has many generators, as well as many
    # ways to combine these generators into more complex ones. Also when it finds failing case it performs
    # so called "shrinking", which means trying to generate minimal possible example that still fails, which
    # greatly helps in understanding what's wrong. I won't import hypothesis here, you can just
    # Google "Python Hypothesis", there are plenty examples on the internet of how tests look. What I'm going
    # to show there is some crude examples of properties that can greatly reduce amount of tests written.

    # Here we rely on generator that can generate any string. In fact to increase probability
    # of edge cases it would be much better to use some custom written generator that definitely
    # includes valid dates as well as just parts of valid dates. Writing such generator is
    # certainly a time investment, but often it pays off very quick. This is an example of
    # "hard to find easy to verify" property pattern
    def property_all_dates_found_should_be_in_original_string(self, any_string):
        actual = self.extract_data(any_string, library.dates_iso8601)
        assert all(date in any_string for date in actual)

    # Relying on another generator, which can share a lot of code with previous one.
    # While one could argue that writing generators can introduce more errors, but
    # as with traditional unit tests bugs in tests are actually captured by production
    # code. And vice verse, of course. Also, writing generator is much more simple
    # task than writing a detector (or even parser).
    def property_valid_dates_should_be_detected(self, string_representing_valid_date):
        actual = self.extract_data(string_representing_valid_date, library.dates_iso8601)
        assert len(actual) == 1
        assert actual[0] == string_representing_valid_date

    def property_valid_dates_should_be_found_in_haystack(self, string_containing_valid_dates):
        actual = self.extract_data(any_string, library.dates_iso8601)
        assert len(actual) > 0

    def property_no_false_positives_should_be_given(self, string_containing_no_valid_date):
        actual = self.extract_data(any_string, library.dates_iso8601)
        assert len(actual) == 0

    # Another common pattern is idempotence. If we modify our extractor function so that it
    # returns string with separators definitely not in dates, then...
    def property_check_extractor_idempotence(self, any_string):
        def extract_helper(source):
            return " | ".join(self.extract_data(source, library.dates_iso8601))
        assert extract_helper(any_string) == extract_helper(extract_helper(any_string))

    # There are many more patterns for properties, like "different paths, same result",
    # "there and back again", "test oracle", "stateful testing" etc. Not all of them are applicable
    # in this small example. Also, in my opinion property based testing doesn't make ordinary
    # "example based testing" obsolete, as examples are very easy for humans to understand and
    # give good starting point. But for finding corner cases I strongly believe property based
    # testing is a way to go. By the way, it's not a new concept, it was first introduced in Haskell
    # by a QuickCheck library, and when in doubt if there is a such framework for your favorite language
    # one can just Google for "quickcheck for <lang>". Hopefully someone will read this...


if __name__ == '__main__':
    unittest.main()
