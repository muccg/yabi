from conf import config
config.read_config()
config.sanitise()

# for SSL context
from OpenSSL import SSL

import os

# for HTTPS, we need a server context factory to build the context for each ssl connection
class ServerContextFactory:
    def getContext(self):
        """Create an SSL context.
        This is a sample implementation that loads a certificate from a file
        called 'server.pem'."""
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_certificate_file(os.path.join(config.config['backend']['certfile']))
        ctx.use_privatekey_file(os.path.join(config.config['backend']['keyfile']))
        return ctx