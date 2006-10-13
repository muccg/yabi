package au.edu.murdoch.ccg.yabi.util.cog;

import java.io.OutputStream;
import java.io.FileOutputStream;

import org.globus.gsi.GlobusCredential;
import org.globus.gsi.CertUtil;
import org.globus.util.Util;
import org.globus.tools.ui.util.UITools;
import org.globus.tools.proxy.GridProxyModel;

public class YabiGridProxyInit {

    private YabiGridProxyModel model = null;
    private GlobusCredential proxy = null;

    private YabiGridProxyModel getModel() {
        return new YabiGridProxyModel();
    }

    public void doStuff (String certFile, String userKey, String password, String proxyFile) {
        model = getModel();

        try {
        proxy = model.createProxy(certFile, userKey, password);
        } catch(Exception e) {
            e.printStackTrace();
            return;
        }

        OutputStream out = null;
        try {
            out = new FileOutputStream(proxyFile);
            Util.setFilePermissions(proxyFile, 600);
            proxy.save(out);
        } catch(Exception e) {
            return;
        } finally {
            if (out != null) {
            try { out.close(); } catch(Exception e) {}
            }
        }

    }

    //static method for testing
    public static void main(String[] args) {
        String certFile = "/export/home/tech/ntakayama/.globus/usercert.pem";
        String userKey = "/export/home/tech/ntakayama/.globus/userkey.pem";
        String proxyFile = "/export/home/tech/ntakayama/proxyThis.hahaha";
        YabiGridProxyInit ygpi = new YabiGridProxyInit();
        ygpi.doStuff(certFile, userKey, args[0], proxyFile);
    }

}
