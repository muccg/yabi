package au.edu.murdoch.ccg.yabi.webservice.actions;

import org.jbpm.graph.def.*;
import org.jbpm.graph.exe.*;
import org.jbpm.*;
import java.util.*;
import java.io.*;
import java.text.SimpleDateFormat;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

import au.edu.murdoch.ccg.yabi.webservice.util.ProcessRunnerThread;
import au.edu.murdoch.ccg.yabi.objects.YabiJobFileInstance;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.util.SymLink;
import au.edu.murdoch.ccg.yabi.util.AppDetails;

import org.apache.commons.configuration.*;

import java.util.logging.Logger;

public class DispatchXML extends BaseAction {

    private static Logger logger;

    public DispatchXML () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        logger = Logger.getLogger( AppDetails.getAppString( request.getContextPath() ) + "." + DispatchXML.class.getName() );
            
        JbpmContext jbpm = jbpmConfiguration.createJbpmContext();

        try {

            //method should be a POST
            if (request.getMethod().compareTo("POST") == 0) {
                //fetch the jobXML param and parse it into a YabiJobFileInstance object
                String jobXML = request.getParameter("jobXML");
                YabiJobFileInstance yjfi = new YabiJobFileInstance();
                yjfi.initFromString(jobXML);

                logger.info("receiving incoming workflow");

                //fetch the process definition and parse it into a JBPM ProcessDefinition object
                String processDefinitionXML = yjfi.getProcessDefinition();
                String definitionName = "";

                ProcessDefinition processDefinition = ProcessDefinition.parseXmlString(processDefinitionXML);
                definitionName = processDefinition.getName();

                //deploy the process definition
                jbpm.getGraphSession().deployProcessDefinition(processDefinition);
                ProcessDefinition pd = jbpm.getGraphSession().findLatestProcessDefinition(definitionName);

                //create a new instance
                ProcessInstance procInstance = new ProcessInstance(pd);

                //fetch the process variables for use when we instantiate a copy of the definition
                Map vars = yjfi.getVariables();
                for(Iterator iter = vars.keySet().iterator(); iter.hasNext(); ) {
                    String key = (String) iter.next();
                    String value = (String) vars.get(key);

                    //skip the cleanup.output.jobStatus and reassign the jobStatus variables
                    if (key.compareTo("cleanup.output.jobStatus") == 0) {
                        yjfi.setVariableForKey("cleanup.output.jobStatus", "");
                        continue;
                    }
                    if (key.compareTo("jobStatus") == 0 &&
                        value.compareTo("completed") == 0) {
                        yjfi.setVariableForKey("jobStatus", "resubmitted");
                        value = "resubmitted";
                    }

                    logger.fine(key + " : " + value);
                    procInstance.getContextInstance().setVariable(key, value);
                }

                //set some higher level variables that will allow our workflow to update the data file
                String userName = yjfi.getUserName();
                String year = yjfi.getYear();
                String month = yjfi.getMonth();
                String jobName = yjfi.getJobName();
                
                procInstance.getContextInstance().setVariable("jobXMLFile", userName + "/jobs/" + year + "-" + month + "/" + jobName + "/workflow.jobxml");
                procInstance.getContextInstance().setVariable("jobDataDir", userName + "/jobs/" + year + "-" + month + "/" + jobName + "/data/");
                procInstance.getContextInstance().setVariable("username", userName);
                procInstance.getContextInstance().setVariable("year", year);
                procInstance.getContextInstance().setVariable("month", month);
                procInstance.getContextInstance().setVariable("jobName", jobName);
                String curTime = new SimpleDateFormat("EEE, d MMM yyyy HH:mm:ss").format( new java.util.Date() ) ;
                procInstance.getContextInstance().setVariable("startTime", curTime );

                //save out slightly modified jobfile
                yjfi.saveFile(userName + "/jobs/" + year + "-" + month + "/" + jobName + "/workflow.jobxml");

                //now that we now the username we can create our initial symlink
                this.createRunningLink(userName, year, month, jobName);

                //transactional save and signal
                //do a transactional close and reopen to save the start 
                jbpm.save(procInstance);
                long procId = procInstance.getId();
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
                request.setAttribute("message", "Process deployment must be performed via a POST operation");
                return mapping.findForward("error");    
            }

        } catch (Exception e) {

            logger.severe("An error occurred while attempting to deploy the definition: ["+e.getClass().getName() +"] "+ e.getMessage());
            request.setAttribute("message", "An error occurred while attempting to deploy the definition: ["+e.getClass().getName() +"] "+ e.getMessage());
            return mapping.findForward("error");

        } finally {
            jbpm.close();
        }

        return mapping.findForward("success");

    }

    private void createRunningLink(String username, String year, String month, String jobName) throws Exception {
        Configuration conf = YabiConfiguration.getConfig();
        String rootDir = conf.getString("yabi.rootDirectory");
        this.checkSymDirs(rootDir, username);

        jobName = jobName.replaceAll(" ", "_");

        String from = rootDir + username + "/jobs/" + year + "-" + month + "/" + jobName;
        String to = rootDir + username + "/.running";

        SymLink.createSymLink(from, to);
    }

    private void checkSymDirs(String rootDir, String username) throws Exception { 
        File runningDir = new File(rootDir + username + "/.running");
        if (!runningDir.exists()) {
            runningDir.mkdir();
        }
        File completedDir = new File(rootDir + username + "/.completed");
        if (!completedDir.exists()) {
            completedDir.mkdir();
        }
    }

}
