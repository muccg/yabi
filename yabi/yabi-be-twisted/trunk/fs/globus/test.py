import CertificateProxy
import GlobusURLCopy

proxy=CertificateProxy.make_proxy()
globus = GlobusURLCopy.GlobusURLCopy()

print globus.WriteToRemote( proxy.ProxyFile("crispin"), "gsiftp://xe-ng2.ivec.org/scratch/bi01/cwellington/destination.txt" )