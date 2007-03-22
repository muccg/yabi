package au.edu.murdoch.cbbc.util;

/**
 * $Id: CBBCException.java,v 1.1 2003/09/16 10:36:36 a.hunter Exp $
 */

import java.io.*;

public class CBBCException extends Throwable {

    private Throwable rootException = null;

    public CBBCException() {
        super();
    }

    public CBBCException(String str) {
        super(str);
    }

    public CBBCException(Throwable t) {
        rootException = t;
    }

    public void printStackTrace(PrintStream p) {
        if (rootException != null) {
            rootException.printStackTrace(p);
        } else {
            super.printStackTrace(p);
        }
    }

    public void printStackTrace(PrintWriter p) {
        if (rootException != null) {
            rootException.printStackTrace(p);
        } else {
            super.printStackTrace(p);
        }
    }

    public String getMessage() {
        String rval = super.getMessage();

        if (rval == null && rootException != null) {
            rval = rootException.getMessage();
        }

        return rval;
    }
}
