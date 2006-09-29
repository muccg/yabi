package au.edu.murdoch.ccg.yabi.webservice.actions;

import org.jbpm.graph.def.*;
import org.jbpm.graph.exe.*;
import org.jbpm.*;
import java.util.*;

import au.edu.murdoch.ccg.yabi.webservice.util.ProcessRunnerThread;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

public class Instantiate extends BaseAction {

    public Instantiate () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        JbpmContext jbpm = jbpmConfiguration.createJbpmContext();

        try {

            //allow for instantiation by id
            long procDefId = Long.parseLong(request.getParameter("id"));

            ProcessDefinition pd = jbpm.getGraphSession().getProcessDefinition( procDefId );

            if (pd != null) {
                ProcessInstance processInstance = new ProcessInstance(pd);

                //set variables according to input
                for (Enumeration e = request.getParameterNames(); e.hasMoreElements(); ) {
                    String curName = (String) e.nextElement();
                    if (curName.compareTo("id") != 0) {
                        processInstance.getContextInstance().setVariable(curName, request.getParameter(curName));
                    }
                }

                //TODO validate that all required inputs exist

                //transactional save and signal
                //do a transactional close and reopen to save the start 
                jbpm.save(processInstance);
                long procId = processInstance.getId();
                jbpm.close();
                jbpm = jbpmConfiguration.createJbpmContext();

                //launch a separate thread so we can push the process along without requiring this thread to wait
                ProcessRunnerThread prt = new ProcessRunnerThread();
                prt.setProcessId( procId );
                prt.setJbpmConfiguration( jbpmConfiguration );
                prt.start();

                //return the process ID
                request.setAttribute("id", new Long(procId));

            } else {
                request.setAttribute("message", "Process definition could not be found");
                return mapping.findForward("error");    
            }

        } catch (Exception e) {

            request.setAttribute("message", "An error occurred while attempting to start the process instance");
            return mapping.findForward("error");

        } finally {
            jbpm.close();
        }

        return mapping.findForward("success");

    }

}
