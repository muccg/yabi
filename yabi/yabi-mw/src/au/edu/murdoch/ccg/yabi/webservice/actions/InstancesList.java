package au.edu.murdoch.ccg.yabi.webservice.actions;

import org.jbpm.graph.def.*;
import org.jbpm.graph.exe.*;
import org.jbpm.*;
import java.util.*;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

import au.edu.murdoch.ccg.yabi.util.*;
import au.edu.murdoch.ccg.yabi.objects.*;

public class InstancesList extends BaseAction {

    public InstancesList () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        //test
        String fname = "ntakayama/jobs/somewhere.jobxml";
        YabiJobFileInstance yjfi = new YabiJobFileInstance(fname);
        yjfi.saveFile();


        JbpmContext jbpm = jbpmConfiguration.createJbpmContext();

        try {
            long procDefId = 0L;
            try {
                procDefId = Long.parseLong(request.getParameter("id"));
            } catch (Exception e) {}

            ProcessDefinition pd = jbpm.getGraphSession().getProcessDefinition( procDefId );

            if (pd != null) {

                request.setAttribute("processDefinition", pd);

                List instances = jbpm.getGraphSession().findProcessInstances( procDefId );
                HashMap tokens = new HashMap();
                HashMap contextVariables = new HashMap();

                Iterator iter = instances.iterator();
                while (iter.hasNext()) {
                    ProcessInstance pi = (ProcessInstance) iter.next();

                    List pitokens = pi.findAllTokens();

                    //force load of node info
                    Iterator tokenIter = pitokens.iterator();
                    while (tokenIter.hasNext()) {
                        Token thisToken = (Token) tokenIter.next();
                        String throwAway = thisToken.getNode().getFullyQualifiedName();
                    }

                    tokens.put( new Long(pi.getId()), pitokens );

                    VariableTranslator vt = new VariableTranslator();
                    contextVariables.put( new Long(pi.getId()),  vt.getVariablesByNode(pi) );
                }

                request.setAttribute("processInstances", instances);
                request.setAttribute("tokens", tokens);
                request.setAttribute("variables", contextVariables);

            } else { //if no process definition for that id

                request.setAttribute("message", "The requested process definition does not exist");
                return mapping.findForward("error");

            }

        } catch (Exception e) {

            e.printStackTrace();
            request.setAttribute("message", "An error occurred while attempting to fetch list of instances for this workflow definition");
            return mapping.findForward("error");

        } finally {
            jbpm.close();
        }

        return mapping.findForward("success");

    }

}
