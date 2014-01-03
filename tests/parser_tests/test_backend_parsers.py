import os
import sys
import re
from nose.tools import nottest
from yabiadmin.backend.torqueparsers import *
from yabiadmin.backend.pbsproparsers import *
from yabiadmin.backend.sgeparsers import *
import logging

TEST_CASES_DIR = os.path.join(os.path.dirname(__file__), 'test_cases')

def create_stdout_handler():
    stdout_handler= logging.StreamHandler()
    stdout_handler.setLevel(logging.DEBUG)
    simple_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdout_handler.setFormatter(simple_formatter)
    return stdout_handler

def setup_root_logger():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(create_stdout_handler())

setup_root_logger()
logger = logging.getLogger(__name__)

# Enable this to see more detail (setup and expectations for each testcase)
#logger.setLevel(logging.DEBUG)


@nottest
def find_test_cases(test_cases_dir):
    all_files = []
    for root, dirs, files in os.walk(test_cases_dir):
        for name in files:
            if name.startswith("."): continue
            full_path = os.path.join(root, name)
            # we use the relative path because it looks better in the test runner output
            rel_path = os.path.relpath(full_path, test_cases_dir)
            all_files.append(rel_path)

    # Uncomment to limit the tests. Some examples:
    #all_files = filter(lambda f: 'torque/qsub/' in f, all_files)
    #all_files = filter(lambda f: 'torque/qsub/test_job_array_submitted_successfully' in f, all_files)

    return all_files


# The function nose will call.
def test():
    for test_case in find_test_cases(TEST_CASES_DIR):
        parser_tester = create_tester(test_case)
        if parser_tester is None:
            logger.warning("No parser tester found for parser '%s'", test_case)
            continue
        yield run_test, test_case, parser_tester


@nottest
def run_test(test_case, tester):
    """Called once for each test_case file"""
    test_case = os.path.join(TEST_CASES_DIR, test_case)
    setup_dict, expectations_dict = tester.parse_testcase(test_case)
    logger.debug('\nTest Case: %s\n%s\n%s', test_case, 
                                            setup_dict, expectations_dict)
    tester.setup(setup_dict)
    tester.act()
    tester.do_assert(expectations_dict)


@nottest
def parse_testcase(test_case):
    contents = None
    try:
        with open(test_case) as f:
            contents = f.read()
        setup, expectations = parse(contents)
        return setup, expectations
    except TestCaseParsingError:
        msg = str(e) or 'unknown'
        logger.warning("Error '%s' while parsing test case '%s'", msg, test_case)
    except Exception, e:
        logger.exception("Couldn't load test_case %s", test_case)
        raise TestCaseParsingError()


def parse(contents):
    DELIMITER = re.compile(r"""
            ^-{5,}  # A line that starts with at least 5 -'s
                    # and has only -'s
            \s*$    # Whitespace at the end of line ignored 
            """, flags=re.MULTILINE | re.VERBOSE)

    parts = re.split(DELIMITER, contents)
    if len(parts) != 2:
        raise TestCaseParsingError("Expected setup and expectations delimited by '-----''s")
    setup_part, expectation_part = parts

    setup = parse_setup(setup_part)
    expectations = parse_expectations(expectation_part)

    return setup, expectations


def sameline_value(name, pattern, lines):
    first_line = lines[0]
    m = re.match(pattern, first_line)
    if m:
        value = m.group(1)
        return name, value

def multiline_value(name, pattern, lines):
    first_line = lines[0]
    m = re.match(pattern, first_line)
    if m:
        value = lines[1:]
        return name, value


def parse_setup(contents):
    to_extract = (
        (sameline_value,  'exit_code', r"^Exit Code\s*:\s*(\d+)"),
        (sameline_value,  'remote_id', r"^remote_id\s*:\s*(\S+)"),
        (multiline_value, 'stdout',    r"^STDOUT\s*:"),
        (multiline_value, 'stderr',    r"^STDERR\s*:"),
    )

    return parse_section(to_extract, contents)

def parse_expectations(contents):
    to_extract = (
        (sameline_value,  'status',    r"^status should be (\S+)"),
        (sameline_value,  'remote_id', r"^remote id should be (\S+)"),
    )

    return parse_section(to_extract, contents)


def parse_section(to_extract, contents):
    """Parses a section of a testcase file (ie. setup or expectations)"""
    group_start_patterns = [x[2] for x in to_extract]
    parsers = [partial(*x) for x in to_extract]

    PATTERNS = [re.compile(p, flags=re.IGNORECASE) for p in group_start_patterns]

    def match(line):
        return any([re.match(p, line) is not None for p in PATTERNS])

    def create_groups(result, line):
        if match(line):
            result.append([])
        if result:
            result[-1].append(line)
        return result

    # Splits up the lines in contents in groups of lines
    # The split occurs on lines that matches any of the PATTERNS
    groups = reduce(create_groups, contents.split('\n'), [])

    def parse_group(lines):
        """Taking a group of lines it tries to parse it with each parser 
        in turn until one parser returns a value"""
        for parse in parsers:
            value = parse(lines)
            if value is not None:
                return value

    values = [parse_group(g) for g in groups]
    values = filter(lambda x: x is not None, values)

    return dict(values)


@nottest
def create_tester(test_case):
    parser_tester = None
    if 'torque/qsub/' in test_case:
        parser_tester = ParserTester(TorqueParser, 'parse_sub', TorqueQSubResult)
    elif 'torque/qstat/' in test_case:
        parser_tester = PollParserTester(TorqueParser, 'parse_poll', TorqueQStatResult)
    elif 'pbspro/qsub/' in test_case:
        parser_tester = ParserTester(PBSProParser, 'parse_sub', PBSProQSubResult)
    elif 'pbspro/qstat/' in test_case:
        parser_tester = PollParserTester(PBSProParser, 'parse_poll', PBSProQStatResult)
    elif 'sge/qsub/' in test_case:
        parser_tester = ParserTester(SGEParser, 'parse_sub', SGEQSubResult)
    elif 'sge/qstat/' in test_case:
        parser_tester = PollParserTester(SGEParser, 'parse_poll', SGEQStatResult)

    return parser_tester


class ParserTester(object):
    def __init__(self, parser_class, method_name, result_class):
        self.parser = parser_class()
        self.method = getattr(self.parser, method_name)
        self.result_class = result_class()

    def __str__(self):
        return "%s.%s:%s" % (
                self.parser.__class__.__module__.replace('yabiadmin.backend.', ''), 
                self.parser.__class__.__name__, 
                self.method.__name__)

    def __repr__(self):
        return self.__str__()

    def parse_testcase(self, test_case):
        return parse_testcase(test_case)

    def map_args(self, setup):
        stdout = setup.get('stdout', [])
        stderr = setup.get('stderr', [])
        exit_code = setup.get('exit_code', 0)
        return [exit_code, stdout, stderr]

    def setup(self, setup_data):
        self.args = self.map_args(setup_data)

    def act(self):
        self.result = self.method(*self.args)

    def do_assert(self, expectations):
        result = self.result
        if 'status' in expectations:
            status = expectations.get('status')
            if not hasattr(self.result_class, status):
                raise RuntimeError("Invalid status: %s" % status)
            expected_status = getattr(self.result_class, status)
            assert result.status == expected_status, "%s != %s" % (result.status, expected_status)
        if 'remote_id' in expectations:
            expected_remote_id = expectations.get('remote_id')
            assert result.remote_id == expected_remote_id, "%s != %s" % (result.remote_id, expected_remote_id)

class PollParserTester(ParserTester):
    def __init__(self, *args):
        ParserTester.__init__(self, *args)

    def map_args(self, setup):
        args = ParserTester.map_args(self, setup)
        remote_id = setup.get('remote_id', [])
        return [remote_id] + args


class TestCaseParsingError(RuntimeError):
    pass

