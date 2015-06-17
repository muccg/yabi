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
from __future__ import unicode_literals
from yabi.backend.fsbackend import FSBackend
from yabi.yabiengine.urihelper import url_join
import logging
logger = logging.getLogger(__name__)


class SelectFileBackend(FSBackend):
    backend_desc = "Select file (\"null\" backend)"
    backend_auth = {}

    def before_stage_in_files(self):
        # For the select backend stage in goes straight to stage out directory.
        # We do not create the working directory.
        # We create the stageout directory and update the stageins with the new destination.
        # The rest of the stagein is the same, so we just rely on the superclass to deal with it.
        stageout_dir = self._create_stageout_dir()
        self._update_stageins_with_new_destination(stageout_dir)

    def stage_out_files(self):
        """No stageout for select file backend"""
        return

    def clean_up_task(self):
        """No clean_up_task for select file backend"""
        return

    # Implementation

    def _create_stageout_dir(self):
        logger.debug('stage_in_files for SelectFileBackend, making stageout {0}'.format(self.task.stageout))
        from yabi.backend.fsbackend import FSBackend
        backend = FSBackend.urifactory(self.yabiusername, self.task.stageout)
        backend.mkdir(self.task.stageout)
        return self.task.stageout

    def _update_stageins_with_new_destination(self, new_destination):
        stageins = self.task.get_stageins()
        for stagein in stageins:
            self._update_stagein_destination(stagein, new_destination)

    def _update_stagein_destination(self, stagein, dst_uri):
        if stagein.src.endswith('/'):
            dst_uri = self.task.stageout
        else:
            filename = stagein.src.rsplit('/', 1)[1]
            dst_uri = url_join(self.task.stageout, filename)

        stagein.dst = dst_uri
        # Destination changed so we have to determine the stagein method again
        stagein.method = self.task.determine_stagein_method(stagein.src, stagein.dst)
        stagein.save()
