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

    public void doStuff (String password) {
        String certFile = "/export/home/tech/ntakayama/.globus/usercert.pem";
        String userKey = "/export/home/tech/ntakayama/.globus/userkey.pem";
        model = getModel();

        try {
        proxy = model.createProxy(certFile, userKey, password);
        } catch(Exception e) {
            e.printStackTrace();
            return;
        }

        OutputStream out = null;
        String proxyFile = "/export/home/tech/ntakayama/proxyThis.hahaha";;
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


    public static void main(String[] args) {
        YabiGridProxyInit ygpi = new YabiGridProxyInit();
        ygpi.doStuff(args[0]);
    }

}
