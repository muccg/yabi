#!/usr/bin/env python

import sys
import glob
import os
import time
import unittest

def run_test(test_file):
    #loader = unittest.defaultTestLoader
    #suite = loader.loadTestsFromName(os.path.splitext(test_file)[0])
    #runner = unittest.TextTestRunner()
    #runner.run(suite)   
    print os.path.splitext(test_file)[0]
    os.system("python -m unittest %s" % 'cookies_test')

def run_all_tests():
    os.system("nosetests")
    #for test_file in glob.glob('*_test.py'):
    #    run_test(test_file)

def anything_changed(since):
    for f in glob.glob('*.py'):
        modified_on = os.path.getmtime(f)
        if modified_on >= since:
            return True
    return False

def main():
    sleep_for = 2 # seconds
    while (True):
        time.sleep(sleep_for)
        if anything_changed(time.time()-sleep_for*2): 
            run_all_tests()

if __name__ == "__main__":
    main()

