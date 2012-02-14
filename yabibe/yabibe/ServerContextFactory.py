# -*- coding: utf-8 -*-
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
        
        #if we are not serving SSL, then the only SSL routines we are using will be HTTPS get and posts. So we don't NEED a certfile. But use it if its there
        #if we are serving SSL, and these aren't set, blowup!
        if config.config['backend']['start_https']:
            assert os.path.exists(os.path.join(config.config['backend']['certfile']))
            assert os.path.exists(os.path.join(config.config['backend']['keyfile']))
            
            ctx.use_certificate_file(os.path.join(config.config['backend']['certfile']))
            ctx.use_privatekey_file(os.path.join(config.config['backend']['keyfile']))
        else:
            # otherwise optional
            if os.path.exists(os.path.join(config.config['backend']['certfile'])):
                ctx.use_certificate_file(os.path.join(config.config['backend']['certfile']))
            if os.path.exists(os.path.join(config.config['backend']['keyfile'])):
                ctx.use_privatekey_file(os.path.join(config.config['backend']['keyfile']))
                
        return ctx