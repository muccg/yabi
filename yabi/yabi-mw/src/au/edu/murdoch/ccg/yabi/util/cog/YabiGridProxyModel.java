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
import org.globus.gsi.GlobusCredentialException;

public class YabiGridProxyModel extends GridProxyModel {
    
    private int bitLength = 512;
    private int expirySeconds = 43200; // 2 months expiry (roughly)
    
    public YabiGridProxyModel(int bitLength, int expirySeconds) {
        super();
        this.bitLength = bitLength;
        this.expirySeconds = expirySeconds;
    }
    
    public YabiGridProxyModel() {
        super();
    }

    public GlobusCredential createProxy(String pwd)
    throws Exception {
        throw new Exception("oops, not implemented");
    }

    public GlobusCredential createProxy(String certFile, String inuserKey, String pwd)  throws Exception {

        userCert = CertUtil.loadCertificate(certFile);
        
        userCert.checkValidity();

        OpenSSLKey key =
            new BouncyCastleOpenSSLKey(inuserKey);

        if (key.isEncrypted()) {
            try {
                key.decrypt(pwd);
            } catch(GeneralSecurityException e) {
                throw new Exception("Wrong password or general security error");
            }
        }

        PrivateKey userKey = key.getPrivateKey();

        BouncyCastleCertProcessingFactory factory =
            BouncyCastleCertProcessingFactory.getDefault();

        int proxyType = (getLimited()) ?
            GSIConstants.DELEGATION_LIMITED :
            GSIConstants.DELEGATION_FULL;


        return factory.createCredential(new X509Certificate[] {userCert},
                userKey,
                bitLength,
                12 * 3600,
                proxyType,
                (org.globus.gsi.X509ExtensionSet) null);
    }


}
