# -*- coding: utf-8 -*-
import CertificateProxy
import GlobusURLCopy
import GlobusRun
from GlobusRun import Run
import GlobusShell
import Auth
import Jobs

# module level "singletons"
Copy = GlobusURLCopy.GlobusURLCopy()
Shell = GlobusShell.GlobusShell()

from RSL import RSL, ConstructRSL, writersltofile
