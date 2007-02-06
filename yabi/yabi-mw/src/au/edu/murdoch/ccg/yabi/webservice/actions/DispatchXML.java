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

import au.edu.murdoch.ccg.yabi.objects.YabiJobFileInstance;

public class DispatchXML extends BaseAction {

    public DispatchXML () {
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
                //fetch the jobXML param and parse it into a YabiJobFileInstance object
                String jobXML = request.getParameter("jobXML");
                YabiJobFileInstance yjfi = new YabiJobFileInstance();
                yjfi.initFromString(jobXML);

                //System.out.println("pd is " + yjfi.getProcessDefinition());

                //fetch the process definition and parse it into a JBPM ProcessDefinition object
                String processDefinitionXML = yjfi.getProcessDefinition();
                String definitionName = "";

                ProcessDefinition processDefinition = ProcessDefinition.parseXmlString(processDefinitionXML);
                definitionName = processDefinition.getName();

                //deploy the process definition
                jbpm.getGraphSession().deployProcessDefinition(processDefinition);
                ProcessDefinition pd = jbpm.getGraphSession().findLatestProcessDefinition(definitionName);

                //create a new instance
                //ProcessInstance procInstance = new ProcessInstance(pd);

                //fetch the process variables for use when we instantiate a copy of the definition
                Map vars = yjfi.getVariables();
                for(Iterator iter = vars.keySet().iterator(); iter.hasNext(); ) {
                    String key = (String) iter.next();
                    String value = (String) vars.get(key);

                    System.out.println(key + " : " + value);
                    //procInstance.getContextInstance().setVariable(key, value);
                }

                //return back the id (although it will probably get ignored)
                request.setAttribute("id", new Long(pd.getId()));

            } else {
                request.setAttribute("message", "Process deployment must be performed via a POST operation");
                return mapping.findForward("error");    
            }

        } catch (Exception e) {

            request.setAttribute("message", "An error occurred while attempting to deploy the definition: ["+e.getClass().getName() +"] "+ e.getMessage());
            return mapping.findForward("error");

        } finally {
            jbpm.close();
        }

        return mapping.findForward("success");

    }

}
