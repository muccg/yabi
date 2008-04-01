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

public class MoveUserspaceFile extends BaseAction {

    private static Logger logger;

    public MoveUserspaceFile () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        logger = Logger.getLogger( AppDetails.getAppString( request.getContextPath() ) + "." + MoveUserspaceFile.class.getName() );
        String outputFormat = request.getParameter("outputformat");

        try {

            Configuration conf = YabiConfiguration.getConfig();
            String rootDirLoc = conf.getString("yabi.rootDirectory");

            //method should be a GET
            if (request.getMethod().compareTo("GET") == 0 &&
                request.getParameter("user") != null &&
                request.getParameter("file") != null &&
                request.getParameter("dest") != null) {

                String user = request.getParameter("user").replaceAll("\\.\\.","");
                String relPath = request.getParameter("file").replaceAll("\\.\\.","");
                String relDestPath = request.getParameter("dest").replaceAll("\\.\\.","");

                String filePath = rootDirLoc + user + "/" + relPath;
                String fileDestPath = rootDirLoc + user + "/" + relDestPath;
                File requestedFile = new File(filePath);
                File destFile = new File(fileDestPath);
                File userDir = new File(rootDirLoc + user);
                
                if (requestedFile.exists() && !destFile.exists()) {

                    if ( destFile.getParentFile().equals(userDir) || requestedFile.getParentFile().equals(userDir) ) {
                        //do not permit moving files from or to the user's top level
                        request.setAttribute("message", "cannot move files to or from your home directory");
                        response.setStatus(HttpServletResponse.SC_CONFLICT);
                        if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                            return mapping.findForward("error");
                        } else {
                            return mapping.findForward("error-txt");
                        }
                    } else {

                        //perform the move
                        requestedFile.renameTo(destFile);

                        return mapping.findForward("success");
                    }
                } else {
                    if (!requestedFile.exists()) {
                        request.setAttribute("message", "requested file does not exist");
                        response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                    } else {
                        request.setAttribute("message", "requested destination name is already in use");
                        response.setStatus(HttpServletResponse.SC_CONFLICT);
                    }

                    if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                        return mapping.findForward("error");
                    } else {
                        return mapping.findForward("error-txt");
                    }
                }

            } else {

                request.setAttribute("message", "move must be performed via a GET operation, and required params must be specified");
                response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                    return mapping.findForward("error");
                } else {
                    return mapping.findForward("error-txt");
                }

            }

        } catch (Exception e) {

            logger.severe("An error occurred while attempting to download file: ["+e.getClass().getName() +"] "+ e.getMessage());
            request.setAttribute("message", "An error occurred while attempting to download file: ["+e.getClass().getName() +"] "+ e.getMessage());
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);

            if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                return mapping.findForward("error");
            } else {
                return mapping.findForward("error-txt");
            }


        }

    }

}
