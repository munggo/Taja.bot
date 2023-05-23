import unittest
import taja


class TestCoreFunctions(unittest.TestCase):
    def test_accuracy(self):
        self.assertEqual(taja._calculate_accuracy("한글", "한글"), 1, "Should be 1")
        #self.assertEqual(taja._calculate_accuracy("한글", "한"), 0.5)
        self.assertEqual(taja._calculate_accuracy("English", "English"), 1)
        #self.assertEqual(taja._calculate_accuracy("cowboy", "boy"), 0.5)

    def test_speed(self):
        self.assertEqual(taja._calculate_speed("한글", 6), 60)


if __name__ == '__main__':
    unittest.main()
