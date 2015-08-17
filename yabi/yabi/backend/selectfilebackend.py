# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
