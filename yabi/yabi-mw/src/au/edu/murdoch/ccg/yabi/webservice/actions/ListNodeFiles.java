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

public class ListNodeFiles extends BaseAction {

    private static Logger logger;

    public ListNodeFiles () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        logger = Logger.getLogger( AppDetails.getAppString( request.getContextPath() ) + "." + ListNodeFiles.class.getName() );
            
        try {

            Configuration conf = YabiConfiguration.getConfig();
            String rootDirLoc = conf.getString("yabi.rootDirectory");
    
            //method should be a GET
            if (request.getMethod().compareTo("GET") == 0 &&
                request.getParameter("user") != null &&
                request.getParameter("year") != null &&
                request.getParameter("month") != null &&
                request.getParameter("jobname") != null &&
                request.getParameter("node") != null) {

                //look for workflow file based on user, year, month and jobname
                String user = request.getParameter("user").replaceAll("\\.\\.","");
                String year = request.getParameter("year").replaceAll("[\\D]","");
                String month = request.getParameter("month").replaceAll("[\\D]","");
                String jobName = request.getParameter("jobname").replaceAll("\\.\\.","");
                String node = request.getParameter("node").replaceAll("\\.\\.","");

                String filePath = rootDirLoc + user + "/jobs/" + year + "-" + month + "/" + jobName + "/data/" + node;
                File requestedFile = new File(filePath);
                
                if (requestedFile.exists() && requestedFile.isDirectory()) {

                    request.setAttribute("files", requestedFile.listFiles(new SafeFileFilter()));
                    return mapping.findForward("success");

                } else {
                    
                    request.setAttribute("message", "requested file does not exist or is a directory");
                    return mapping.findForward("error");
                }

            } else {

                request.setAttribute("message", "download must be performed via a GET operation, and required params must be specified");
                return mapping.findForward("error");    

            }

        } catch (Exception e) {

            logger.severe("An error occurred while attempting to download file: ["+e.getClass().getName() +"] "+ e.getMessage());
            request.setAttribute("message", "An error occurred while attempting to download file: ["+e.getClass().getName() +"] "+ e.getMessage());
            return mapping.findForward("error");

        }

    }

}

class SafeFileFilter implements FileFilter {

    public boolean accept (File pathname) {
        if (pathname.exists() && pathname.isFile()) return true;
        return false;
    }

}
