import sys

PRE = """
{
    "name": "hostname",
    "tags": [],
    "jobs": [{"""

HOSTNAME = """
            "toolName":"hostname",
            "jobId":%s,
            "valid":true,
            "parameterList":{
                "parameter":[]
            }
"""

POST = """        }]
}
"""

def hostname(how_many):
    hostnames = HOSTNAME % 1
    i = 2
    while i <= how_many:
        hostnames = (" " * 8 + "},{").join([hostnames, HOSTNAME % i])
        i += 1
    print "".join([PRE, hostnames, POST])    

def main():
    count = 1
    if len(sys.argv) == 2:
        count = int(sys.argv[1])
    hostname(count)

if __name__ == "__main__":
    main()

