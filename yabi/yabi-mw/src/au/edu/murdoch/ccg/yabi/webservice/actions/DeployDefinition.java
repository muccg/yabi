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

public class DeployDefinition extends BaseAction {

    public DeployDefinition () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        JbpmContext jbpm = jbpmConfiguration.createJbpmContext();

        try {

            //method should be a POST
            if (request.getMethod().compareTo("POST") == 0) {

                String processDefinitionXML = request.getParameter("definition");
                String definitionName = "";

                ProcessDefinition processDefinition = ProcessDefinition.parseXmlString(processDefinitionXML);
                definitionName = processDefinition.getName();

                jbpm.getGraphSession().deployProcessDefinition(processDefinition);
                ProcessDefinition pd = jbpm.getGraphSession().findLatestProcessDefinition(definitionName);

                request.setAttribute("id", new Long(pd.getId()));

            } else {
                request.setAttribute("message", "Process deployment must be performed via a POST operation");
                return mapping.findForward("error");    
            }

        } catch (Exception e) {

            request.setAttribute("message", "An error occurred while attempting to deploy the definition");
            return mapping.findForward("error");

        } finally {
            jbpm.close();
        }

        return mapping.findForward("success");

    }

}
