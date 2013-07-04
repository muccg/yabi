### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
from yabiadmin.backend.fsbackend import FSBackend
from yabiadmin.yabiengine.enginemodels import StageIn
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.backend.utils import create_fifo
from yabiadmin.backend.parsers import parse_ls
from yabiadmin.yabiengine.urihelper import uriparse, url_join
import traceback
import logging
logger = logging.getLogger(__name__)

class SelectFileBackend(FSBackend):

    def stage_in_files(self):
        """
        For the select backend stage in goes straight to stage out directory.
        We do not create the working directory.
        """
        # we need to make the stageout directory so we can push the stage in files straight there
        logger.debug('stage_in_files for SelectFileBackend, making stageout {0}'.format(self.task.stageout))
        from yabiadmin.backend.fsbackend import FSBackend
        backend = FSBackend.urifactory(self.yabiusername, self.task.stageout)
        backend.mkdir(self.task.stageout)
 
        # do the stage in
        stageins = StageIn.objects.filter(task=self.task).order_by('order')
        for stagein in stageins:
            self.stage_in(stagein)

    def stage_in(self, stagein):
        """ For the select backend stage in goes straight to stage out directory"""
        logger.debug('SelectFileBackend.stage_in {0} {1}'.format(stagein.method, stagein.src))
        logger.debug(stagein.method)
       
        # we need to create the path to the destination file in the stageout area for the file copy 
        filename = stagein.src.rsplit('/',1)[1]
        dst_uri = url_join(self.task.stageout, filename)

        if stagein.method == 'copy':
            if stagein.src.endswith('/'):
                return FSBackend.remote_copy(self.yabiusername, stagein.src, dst_uri)
            else:
                return FSBackend.remote_file_copy(self.yabiusername, stagein.src, dst_uri)

        if stagein.method == 'lcopy':
            raise NotImplementedError("No lcopy for SelectFileBackend")

        if stagein.method == 'link':
            raise NotImplementedError("No link for SelectFileBackend")

    def stage_out_files(self):
        """No stageout for select file backend"""
        return

    def clean_up_task(self):
        """No clean_up_task for select file backend"""
        return
