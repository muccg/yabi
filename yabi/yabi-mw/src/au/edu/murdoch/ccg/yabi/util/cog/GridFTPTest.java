package au.edu.murdoch.ccg.yabi.util.cog;

import org.globus.ftp.*;
import org.globus.gsi.*;
import org.ietf.jgss.GSSCredential;
import org.globus.gsi.gssapi.GlobusGSSCredentialImpl;

public class GridFTPTest {

    public static void main(String[] args) {
        try {
            GridFTPClient client = new GridFTPClient(args[0], Integer.parseInt(args[1]));

            GSSCredential credential;
            GlobusCredential globusCredential;

            globusCredential = new GlobusCredential( args[2] );
            credential = new GlobusGSSCredentialImpl( globusCredential, GSSCredential.INITIATE_AND_ACCEPT );    

            ((GridFTPClient)client).authenticate(credential);

            System.out.println("connected, listing shows: " + client.list());

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
