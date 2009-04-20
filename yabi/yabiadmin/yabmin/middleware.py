from django.db import connection

class Logging:
    def process_response(self, request, response):
        for query in connection.queries:
            print "\033[1;31m[%s]\033[0m \033[1m%s\033[0m" % (query['time'], " ".join(query['sql'].split()))
        return response
