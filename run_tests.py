import unittest


def testsuite():
    from tests import tests

    suite = unittest.TestSuite()
    suite.addTest(tests.suite())
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(testsuite())
