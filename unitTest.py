# main.py

import unittest
import main

# def getSol(file):
#     sol = False
#     solution_list = []
#     with open(file, 'r') as f:
#         for line in f:
#             if line.startswith('# Tiles Problem Solution Key'):
#                 f.readline()
#                 sol = True
#                 continue
#             if sol and len(solution_list) < 25:
#                 solution_list.append(line[:-1])
#     return solution_list

class TestMethods(unittest.TestCase):

    def test_example1(self):
        file = 'testcases/testcase1.txt'
        result = main.main(file)

        self.assertEqual(len(result), 25)

    def test_example2(self):
        file = 'testcases/testcase2.txt'
        result = main.main(file)

        self.assertEqual(len(result), 25)

    def test_example3(self):
        file = 'testcases/testcase3.txt'
        result = main.main(file)

        self.assertEqual(len(result), 25)

    def test_example4(self):
        file = 'testcases/testcase4.txt'
        result = main.main(file)

        self.assertEqual(len(result), 25)

    def test_example5(self):
        file = 'testcases/testcase5.txt'
        result = main.main(file)

        self.assertEqual(len(result), 25)

    def test_example6(self):
        file = 'testcases/testcase6.txt'
        result = main.main(file)

        self.assertEqual(len(result), 25)

    def test_example7(self):
        file = 'testcases/testcase7.txt'
        result = main.main(file)

        self.assertEqual(len(result), 25)

    def test_example8(self):
        file = 'testcases/testcase8.txt'
        result = main.main(file)

        self.assertEqual(len(result), 25)

    def test_example9(self):
        file = 'testcases/testcase9.txt'
        result = main.main(file)

        self.assertEqual(len(result), 25)

    def test_example10(self):
        file = 'testcases/testcase10.txt'
        result = main.main(file)

        self.assertEqual(len(result), 25)

if __name__ == '__main__':
    unittest.main()