from CertificateProxy import CertificateProxy
import GlobusURLCopy
import GlobusRun
import GlobusShell
import Auth
import Jobs

# module level "singletons"
Copy = GlobusURLCopy.GlobusURLCopy()
Run = GlobusRun.GlobusRun()
Shell = GlobusShell.GlobusShell()

# shortcuts to classes
Auth = Auth.GlobusAuth

from RSL import RSL, ConstructRSL, writersltofile
