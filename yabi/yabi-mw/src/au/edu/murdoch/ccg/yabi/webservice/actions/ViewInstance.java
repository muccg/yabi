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

public class ViewInstance extends BaseAction {

    public ViewInstance () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        JbpmContext jbpm = jbpmConfiguration.createJbpmContext();

        try {
            long procInstId = Long.parseLong(request.getParameter("id"));

            ProcessInstance pi = jbpm.getGraphSession().getProcessInstance( procInstId );

            if (pi != null) {

                request.setAttribute("processInstance", pi);

                //force load of process definition
                ProcessDefinition processDefinition = pi.getProcessDefinition();
                String forceName = processDefinition.getName();
                request.setAttribute("processDefinition", processDefinition);
                //force load of all tokens
                List tokens = pi.findAllTokens();
                Iterator iter = tokens.iterator();
                while (iter.hasNext()) {
                    Token tempForce = (Token) iter.next();
                    String nodeForce = tempForce.getNode().getName();
                }
                request.setAttribute("tokens", tokens);
                Map contextVariables = pi.getContextInstance().getVariables();
                request.setAttribute("contextVariables", contextVariables);

            } else { //if no process instance for that id

                request.setAttribute("message", "The requested process instance does not exist");
                return mapping.findForward("error");

            }

        } catch (Exception e) {

            request.setAttribute("message", "An error occurred while attempting to fetch a process instance");
            return mapping.findForward("error");

        } finally {
            jbpm.close();
        }

        return mapping.findForward("success");

    }

}
