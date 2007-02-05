package au.edu.murdoch.ccg.yabi.util.cog;

import org.globus.ftp.*;
import org.globus.gsi.*;
import org.ietf.jgss.GSSCredential;
import org.globus.gsi.gssapi.GlobusGSSCredentialImpl;
import java.io.*;

public class GridFTPTest {

    public static void main(String[] args) {
        try {
            GridFTPClient client = new GridFTPClient(args[0], Integer.parseInt(args[1]));

            GSSCredential credential;
            GlobusCredential globusCredential;

            globusCredential = new GlobusCredential( args[2] );
            credential = new GlobusGSSCredentialImpl( globusCredential, GSSCredential.INITIATE_AND_ACCEPT );    

            ((GridFTPClient)client).authenticate(credential);

            System.out.println("connected");

            client.setDataChannelProtection(GridFTPSession.PROTECTION_PRIVATE);
            System.out.println("dcp = " + client.getDataChannelProtection());

            System.out.println("listing shows: " + client.list());

            //put a file
            client.put(new File("/export/home/tech/ntakayama/outgoing/payload"), "/export/home/tech/ntakayama/payload", false);

            //fetch the same file
            client.get("/export/home/tech/ntakayama/payload", new File("/export/home/tech/ntakayama/incoming/payload"));

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
