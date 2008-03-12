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

public class ListRunningJobs extends BaseAction {

    private static Logger logger;

    public ListRunningJobs () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        logger = Logger.getLogger( AppDetails.getAppString( request.getContextPath() ) + "." + ListRunningJobs.class.getName() );
        String outputFormat = request.getParameter("outputformat"); 
        if (outputFormat == null) {
            outputFormat = TYPE_XML;
        }
           
        try {

            Configuration conf = YabiConfiguration.getConfig();
            String rootDirLoc = conf.getString("yabi.rootDirectory");
    
            //method should be a GET
            if (request.getMethod().compareTo("GET") == 0 &&
                request.getParameter("user") != null 
                ) {

                String user = request.getParameter("user").replaceAll("\\.\\.","");

                String filePath = rootDirLoc + user + "/.running";
                File requestedFile = new File(filePath);
                
                if (requestedFile.exists() && requestedFile.isDirectory()) {

                    File[] files = requestedFile.listFiles(new SafeUserFileFilter());
                    //contents of .running and .completed folders are symlinks that are renamed to year_month_jobname
                    ArrayList jobs = new ArrayList();

                    for (int i=0; i<files.length; i++) {
                        String[] parts = files[i].getName().split("_",3);
                        HashMap map = new HashMap();
                        map.put("year", parts[0]);
                        map.put("month", parts[1]);
                        map.put("name", parts[2]);
                        jobs.add(map);
                    }
                    request.setAttribute("jobs", jobs);

                    if (outputFormat.compareTo(TYPE_TXT) != 0) {
                        return mapping.findForward("success");
                    } else {
                        return mapping.findForward("success-txt");
                    }

                } else {
                    
                    request.setAttribute("message", "requested file does not exist or is a directory");
                    response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                    if (outputFormat.compareTo(TYPE_TXT) != 0) {
                        return mapping.findForward("error");
                    } else {
                        return mapping.findForward("error-txt");
                    }
                }

            } else {

                request.setAttribute("message", "list must be performed via a GET operation, and required params must be specified");
                response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                if (outputFormat.compareTo(TYPE_TXT) != 0) {
                    return mapping.findForward("error");
                } else {
                    return mapping.findForward("error-txt");
                }

            }

        } catch (Exception e) {

            logger.severe("An error occurred while attempting to list jobs: ["+e.getClass().getName() +"] "+ e.getMessage());
            request.setAttribute("message", "An error occurred while attempting to list jobs: ["+e.getClass().getName() +"] "+ e.getMessage());
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            if (outputFormat.compareTo(TYPE_TXT) != 0) {
                return mapping.findForward("error");
            } else {
                return mapping.findForward("error-txt");
            }

        }

    }

}

