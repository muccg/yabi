package au.edu.murdoch.ccg.yabi.webservice.actions;

import java.util.*;
import java.io.*;

import java.text.SimpleDateFormat;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.ServletOutputStream;

import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

import au.edu.murdoch.ccg.yabi.objects.YabiJobFileInstance;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.util.SymLink;
import au.edu.murdoch.ccg.yabi.util.AppDetails;

import org.apache.commons.configuration.*;

import java.util.logging.Logger;

public class Status extends BaseAction {

    private static Logger logger;

    public Status () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        logger = Logger.getLogger( AppDetails.getAppString( request.getContextPath() ) + "." + Status.class.getName() );
            
        try {

            Configuration conf = YabiConfiguration.getConfig();
            String rootDirLoc = conf.getString("yabi.rootDirectory");
    
            //method should be a GET
            if (request.getMethod().compareTo("GET") != 0) {
                request.setAttribute("message", "status check must be performed via a GET operation");
                response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                return mapping.findForward("error");    
            }

            //look for workflow file based on user, year, month and jobname
            String user = request.getParameter("user").replaceAll("\\.\\.","");
            String year = request.getParameter("year").replaceAll("[\\D]","");
            String month = request.getParameter("month").replaceAll("[\\D]","");
            String jobName = request.getParameter("jobname").replaceAll("\\.\\.","");
            String outputFormat = request.getParameter("outputformat");
            if (outputFormat != null) {
                outputFormat.replaceAll("\\.\\.","");
            }
            String nodeName= request.getParameter("nodename");
            if (nodeName!= null) {
                nodeName.replaceAll("\\.\\.","");
            }

            String filePath = user + "/jobs/" + year + "-" + month + "/" + jobName + "/workflow.jobxml";
            File jobFile = new File(rootDirLoc + filePath);
            
            // no workflow file, bomb out
            if (!jobFile.exists()) {
                request.setAttribute("message", "requested job does not exist");
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                return mapping.findForward("error");
            }

            // if not output format set, or if its not set to TYPE_TXT, we spew out xml
            if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                FileInputStream fileToDownload = new FileInputStream(rootDirLoc + filePath);
                ServletOutputStream out = response.getOutputStream();

                response.setContentType("text/xml");

                int c;
                while((c=fileToDownload.read()) != -1){
                    out.write(c);
                }
                out.flush();
                out.close();
                fileToDownload.close();
                return null;
            } else {
                YabiJobFileInstance yFile = new YabiJobFileInstance(filePath);
                String jobStatusStr = null;
                String errorMessage = null;
                if (nodeName != null) {
                    jobStatusStr = yFile.getVariableByKey(nodeName + "-check.output.jobStatus");
                    errorMessage = yFile.getVariableByKey(nodeName + "-check.output.errorMessage");
                    if (jobStatusStr == null || jobStatusStr.compareTo("") == 0) {
                        jobStatusStr = yFile.getVariableByKey(nodeName + ".output.jobStatus");
                        errorMessage = yFile.getVariableByKey(nodeName + ".output.errorMessage");
                    }
                } else {
                    jobStatusStr = yFile.getVariableByKey("cleanup.output.jobStatus");
                    errorMessage = yFile.getVariableByKey("cleanup.output.errorMessage");
                }

                if (jobStatusStr == null || jobStatusStr.length() == 0) {
                    request.setAttribute("message", "Unknown job status");
                    response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
                    return mapping.findForward("error");
                }
            
                if (errorMessage == null) {
                    errorMessage = "";
                }

                response.setContentType("text/plain");
                ServletOutputStream out = response.getOutputStream();
                out.print(jobStatusStr + "\n" + errorMessage);
                out.flush();
                out.close();
                return null;
            }


        } catch (Exception e) {

            logger.severe("An error occurred while attempting to download file: ["+e.getClass().getName() +"] "+ e.getMessage());
            request.setAttribute("message", "An error occurred while attempting to download file: ["+e.getClass().getName() +"] "+ e.getMessage());
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            return mapping.findForward("error");

        }

    }

}
