import unittest
import taja
import time
from model import Participant


class TestCoreFunctions(unittest.TestCase):
    def test_accuracy(self):
        self.assertEqual(taja._calculate_accuracy("한글", "한글"), 1, "Should be 1")
        #self.assertEqual(taja._calculate_accuracy("한글", "한"), 0.5)
        self.assertEqual(taja._calculate_accuracy("English", "English"), 1)
        #self.assertEqual(taja._calculate_accuracy("cowboy", "boy"), 0.5)

    def test_speed(self):
        self.assertEqual(taja._calculate_speed("한글", 6), 60)

    def test_duplicated_participation_in_a_game(self):
        participants = [
                Participant(id="user A", accuracy=50, wpm=100, time_entered=time.time(), score=0),
                Participant(id="user B", accuracy=100, wpm=100, time_entered=time.time(), score=0),
                Participant(id="user A", accuracy=100, wpm=100, time_entered=time.time(), score=0)
        ]
        self.assertEqual(taja._has_participated(participants, "user A"), True)
        self.assertEqual(taja._has_participated(participants, "user B"), True)
        self.assertEqual(taja._has_participated(participants, "user C"), False)


if __name__ == '__main__':
    unittest.main()
