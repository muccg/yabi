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

public class DefinitionsList extends BaseAction {

    public DefinitionsList () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        JbpmContext jbpm = jbpmConfiguration.createJbpmContext();

        List processDefs = new ArrayList();

        try {

            processDefs = jbpm.getGraphSession().findLatestProcessDefinitions();
    
        } catch (Exception e) {

            request.setAttribute("message", "An error occurred while attempting to fetch the process definition list");
            return mapping.findForward("error");

        } finally {
            jbpm.close();
        }

        request.setAttribute("processDefinitions", processDefs);

        return mapping.findForward("success");

    }

}
