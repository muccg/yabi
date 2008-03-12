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

public class ListUserspaceFiles extends BaseAction {

    private static Logger logger;

    public ListUserspaceFiles () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        logger = Logger.getLogger( AppDetails.getAppString( request.getContextPath() ) + "." + ListUserspaceFiles.class.getName() );
        String outputFormat = request.getParameter("outputformat"); 
        if (outputFormat == null) {
            outputFormat = TYPE_XML;
        }
           
        try {

            Configuration conf = YabiConfiguration.getConfig();
            String rootDirLoc = conf.getString("yabi.rootDirectory");
    
            //method should be a GET
            if (request.getMethod().compareTo("GET") == 0 &&
                request.getParameter("user") != null &&
                request.getParameter("path") != null ) {

                //look for workflow file based on user, year, month and jobname
                String user = request.getParameter("user").replaceAll("\\.\\.","");
                String path = request.getParameter("path").replaceAll("\\.\\.","");

                String filePath = rootDirLoc + user + "/" + path;
                File requestedFile = new File(filePath);
                
                if (requestedFile.exists() && requestedFile.isDirectory()) {

                    request.setAttribute("files", requestedFile.listFiles(new SafeUserFileFilter()));
                    if (outputFormat.compareTo(TYPE_TXT) != 0) {
                        return mapping.findForward("success");
                    } else {
                        return mapping.findForward("success-txt");
                    }

                } else {
                    
                    request.setAttribute("message", "requested file does not exist or is not a directory");
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

            logger.severe("An error occurred while attempting to list files: ["+e.getClass().getName() +"] "+ e.getMessage());
            request.setAttribute("message", "An error occurred while attempting to list files: ["+e.getClass().getName() +"] "+ e.getMessage());
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            if (outputFormat.compareTo(TYPE_TXT) != 0) {
                return mapping.findForward("error");
            } else {
                return mapping.findForward("error-txt");
            }

        }

    }

}

class SafeUserFileFilter implements FileFilter {

    public boolean accept (File pathname) {
        if (pathname.exists() && (pathname.isFile() || pathname.isDirectory()) && !pathname.isHidden()) return true;
        return false;
    }

}
