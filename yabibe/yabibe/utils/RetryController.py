#
# RetryController
# 
# this is a class that assists in determining if a subprocess has failed permanently
# or temporarily. It does not deal with success. Only if failures are 'soft' or 'hard'
#

HARD = 1
SOFT = 0


import re


class RetryController(object):
    default = SOFT                              # when no firm decision can be made, go with this
    
    hard_exit_codes = []                        # any exit with this code is hard exit
    
    soft_exit_codes = []                        # any exit with this code is soft exit
    
    # the format of the following dictionaries
    # key: the exit code
    # value: a list of regular expression matches
    
    hard_exit_regexps = {}                      # regular expressions to determine finer grained status based on output          
    soft_exit_regexps = {}
    
    def __init__(self):
        pass

    def compile_all_regexps(self):
        self.hard_exit_regexps = self.compile_regexps(self.hard_exit_regexps)
        self.soft_exit_regexps = self.compile_regexps(self.soft_exit_regexps)
        
    def compile_regexps(self, struct, flags=0):
        out = {}
        for code,regexp_list in struct:
            out[code] = []
            for re_item in regexp_list:
                out[code].append( re.compile( re_item, flags ) )
        return out
        
    def test(self, exit_code, stderr):
        """Test the resturn values from a programme run and return HARD or SOFT"""
        if exit_code in self.hard_exit_codes:
            return HARD
        
        if exit_code in self.soft_exit_codes:
            return SOFT
            
        if exit_code in self.hard_exit_regexps:
            # test regexps
            for regexp in self.hard_exit_regexps[exit_code]:
                match = regexp.search(stderr)
                if match is not None:
                    return HARD
                    
        if exit_code in self.soft_exit_regexps:
            # test regexps
            for regexp in self.soft_exit_regexps[exit_code]:
                match = regexp.search(stderr)
                if match is not None:
                    return SOFT
                    
        return self.default
             
    
    
class PbsProRetryController(RetryController):
    default = SOFT
    hard_exit_codes = [1]
    soft_exit_codes = [188]
    
    hard_exit_regexps = {   2: [
                                r'a single - is no a valid option',                       #typo exists in error code in torque sourcecode
                                r'qsub: illegal -\w value',
                                r'qsub: Must be the super user to submit a proxy job',
                                r'qsub: -P requires a user name',
                                r'qsub: error parsing -\w value',
                                r'qsub: illegal -W. job_radix must be',
                                r'qsub: DISPLAY not set',
                                r'The -J option can only be used in conjunction with -P',
                                r'index issues',
                                r'qsub: Failed to get xauth data',
                                r'qsub: cannot form a valid job name from the script name'
                            ],
                            1: [
                            ]
                        }
    
    
    
    

