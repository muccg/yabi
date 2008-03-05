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
            if (request.getMethod().compareTo("GET") == 0) {

                //look for workflow file based on user, year, month and jobname
                String user = request.getParameter("user").replaceAll("\\.\\.","");
                String year = request.getParameter("year").replaceAll("[\\D]","");
                String month = request.getParameter("month").replaceAll("[\\D]","");
                String jobName = request.getParameter("jobname").replaceAll("\\.\\.","");

                String filePath = rootDirLoc + user + "/jobs/" + year + "-" + month + "/" + jobName + "/workflow.jobxml";
                File jobFile = new File(filePath);
                
                if (jobFile.exists()) {

                    FileInputStream fileToDownload = new FileInputStream(filePath);
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
                    
                    request.setAttribute("message", "requested job does not exist");
                    return mapping.findForward("error");
                }

            } else {

                request.setAttribute("message", "status check must be performed via a GET operation");
                return mapping.findForward("error");    

            }

        } catch (Exception e) {

            logger.severe("An error occurred while attempting to download file: ["+e.getClass().getName() +"] "+ e.getMessage());
            request.setAttribute("message", "An error occurred while attempting to download file: ["+e.getClass().getName() +"] "+ e.getMessage());
            return mapping.findForward("error");

        }

    }

}
