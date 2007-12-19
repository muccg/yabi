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
    private String proxyPath = "";
    private int expirySeconds = 30 * 24 * 3600;
    private int bits = 512;
    
    public YabiGridProxyInit () {
    }
    
    public YabiGridProxyInit (int expiry) {
        this.expirySeconds = expiry;
    }

    private YabiGridProxyModel getModel() {
        return new YabiGridProxyModel(this.bits, this.expirySeconds);
    }
    
    public void verifyProxy (String proxyFile) throws Exception {
        GlobusCredential globusCredential;
        globusCredential = new GlobusCredential( proxyFile );
        
        globusCredential.verify();
        
        this.proxy = globusCredential;
    }
        
    public void initProxy (String certFile, String userKey, String password, String proxyFile) throws Exception {
        model = getModel();

        proxy = model.createProxy(certFile, userKey, password);

        this.proxyPath = proxyFile;
        
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
    
    public String getProxyPath() {
        return this.proxyPath;
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
