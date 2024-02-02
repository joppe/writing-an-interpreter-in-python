import unittest

from interpreter import object


class TestObject(unittest.TestCase):
    def test_string_hash_key(self) -> None:
        hello1 = object.String("Hello World")
        hello2 = object.String("Hello World")
        diff1 = object.String("My name is johnny")
        diff2 = object.String("My name is johnny")

        self.assertEqual(hello1.hash_key(), hello2.hash_key())
        self.assertEqual(diff1.hash_key(), diff2.hash_key())
        self.assertNotEqual(hello1.hash_key(), diff1.hash_key())
