"""
Run all unit tests for the python plugin
"""
import os
import unittest
import sys

def suite():
    # Load the unit tests
    test_loader = unittest.TestLoader()
    path = os.path.dirname(__file__)
    suite = test_loader.discover(path, pattern="test_*.py")

    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2, failfast=True)
    r = not runner.run(suite()).wasSuccessful()
    sys.exit(r)
