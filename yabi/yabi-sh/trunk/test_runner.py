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

def any_files_changed_since(time):
    for f in glob.glob('**/*.py'):
        modified_on = os.path.getmtime(f)
        if modified_on >= time:
            return True
    return False

def sleep_for(secs):
    time.sleep(secs)

def main():
    while (True):
        before_sleep = time.time()-1
        sleep_for(2) # seconds
        if any_files_changed_since(before_sleep): 
            run_all_tests()

if __name__ == "__main__":
    main()

