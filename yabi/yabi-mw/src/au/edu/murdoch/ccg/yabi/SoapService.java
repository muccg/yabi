package au.edu.murdoch.ccg.yabi;

/**
 * $Id: SoapService.java, $Revision $
 */

import java.util.*;
import org.apache.axis.*;
import javax.xml.soap.*;
import javax.activation.*;
import org.xml.sax.InputSource;

public class SoapService {

    public SoapService() {}

    public boolean isAlive() {
        return true;
    }

}
