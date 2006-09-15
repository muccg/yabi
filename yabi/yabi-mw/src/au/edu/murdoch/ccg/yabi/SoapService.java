package au.edu.murdoch.ccg.yabi;

/**
 * $Id: SoapService.java, $Revision $
 */

import java.util.*;
import org.apache.axis.*;
import javax.xml.soap.*;
import javax.activation.*;
import org.xml.sax.InputSource;

import org.jbpm.graph.def.*;
import org.jbpm.graph.exe.*;
import org.jbpm.*;

public class SoapService {

    public SoapService() {}

    public boolean isAlive() {
        return true;
    }

    public String getDefinitions() {
        JbpmConfiguration jbpmConfiguration = JbpmConfiguration.getInstance();
        ArrayList definitions = new ArrayList();
        String output = "";

        JbpmContext jbpm = jbpmConfiguration.createJbpmContext();

        try {
            List processDefs = jbpm.getGraphSession().findLatestProcessDefinitions();

            Iterator iter = processDefs.iterator();
            while (iter.hasNext()) {
                ProcessDefinition pd = (ProcessDefinition) iter.next();
                definitions.add(pd.getName());
                output += pd.getName() + ", ";
            }
        } catch (Exception e) {
        } finally {
            jbpm.close();
        }

        return output;
    }
}
