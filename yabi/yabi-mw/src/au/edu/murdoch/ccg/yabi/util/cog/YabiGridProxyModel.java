package au.edu.murdoch.ccg.yabi.util.cog;

import java.security.PrivateKey;
import java.security.GeneralSecurityException;
import java.security.cert.X509Certificate;

import org.globus.gsi.CertUtil;
import org.globus.gsi.OpenSSLKey;
import org.globus.gsi.GlobusCredential;
import org.globus.gsi.GSIConstants;
import org.globus.gsi.bc.BouncyCastleOpenSSLKey;
import org.globus.gsi.bc.BouncyCastleCertProcessingFactory;
import org.globus.tools.proxy.GridProxyModel;

public class YabiGridProxyModel extends GridProxyModel {

    public GlobusCredential createProxy(String pwd)
    throws Exception {
        throw new Exception("oops, not implemented");
    }

    public GlobusCredential createProxy(String certFile, String inuserKey, String pwd)  throws Exception {

        userCert = CertUtil.loadCertificate(certFile);

        OpenSSLKey key =
            new BouncyCastleOpenSSLKey(inuserKey);

        if (key.isEncrypted()) {
            try {
                key.decrypt(pwd);
            } catch(GeneralSecurityException e) {
                throw new Exception("Wrong password or other security error");
            }
        }

        PrivateKey userKey = key.getPrivateKey();

System.out.println("Arrgh 1");
        BouncyCastleCertProcessingFactory factory =
            BouncyCastleCertProcessingFactory.getDefault();

        int proxyType = (getLimited()) ?
            GSIConstants.DELEGATION_LIMITED :
            GSIConstants.DELEGATION_FULL;
System.out.println("Arrgh 2");
        return factory.createCredential(new X509Certificate[] {userCert},
                userKey,
                128,
                1 * 3600,
                proxyType,
                (org.globus.gsi.X509ExtensionSet) null);
    }


}
