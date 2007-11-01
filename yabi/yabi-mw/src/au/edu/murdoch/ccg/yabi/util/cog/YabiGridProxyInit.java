package au.edu.murdoch.ccg.yabi.util.cog;

import java.io.OutputStream;
import java.io.FileOutputStream;

import org.globus.gsi.GlobusCredential;
import org.globus.gsi.CertUtil;
import org.globus.util.Util;
import org.globus.tools.ui.util.UITools;
import org.globus.tools.proxy.GridProxyModel;
import org.globus.gsi.GlobusCredentialException;

public class YabiGridProxyInit {

    private YabiGridProxyModel model = null;
    private GlobusCredential proxy = null;

    private YabiGridProxyModel getModel() {
        return new YabiGridProxyModel();
    }
    
    public void verifyProxy (String proxyFile) throws Exception {
        GlobusCredential globusCredential;
        globusCredential = new GlobusCredential( proxyFile );
        
        globusCredential.verify();
    }
        
    public void initProxy (String certFile, String userKey, String password, String proxyFile) throws Exception {
        model = getModel();

        proxy = model.createProxy(certFile, userKey, password);

        OutputStream out = null;
        try {
            out = new FileOutputStream(proxyFile);
            Util.setFilePermissions(proxyFile, 600);
            proxy.save(out);
        } catch(Exception e) {
            throw e; //propagate the exception
        } finally {
            if (out != null) {
            try { out.close(); } catch(Exception e) {}
            }
        }

    }

    //static method for testing
    /* public static void main(String[] args) {
        String certFile = "/export/home/tech/ntakayama/.globus/usercert.pem";
        String userKey = "/export/home/tech/ntakayama/.globus/userkey.pem";
        String proxyFile = "/export/home/tech/ntakayama/proxyThis.hahaha";
        YabiGridProxyInit ygpi = new YabiGridProxyInit();
        ygpi.initProxy(certFile, userKey, args[0], proxyFile);
    }
     */
}
