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

public class CopyUserspaceFile extends BaseAction {

    private static Logger logger;

    public CopyUserspaceFile () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        logger = Logger.getLogger( AppDetails.getAppString( request.getContextPath() ) + "." + CopyUserspaceFile.class.getName() );
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
                        request.setAttribute("message", "cannot copy files to or from your home directory");
                        response.setStatus(HttpServletResponse.SC_FORBIDDEN);
                        if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                            return mapping.findForward("error");
                        } else {
                            return mapping.findForward("error-txt");
                        }
                    } else {

                        //perform the copy
                        boolean success = true;
                        try {
                            copyFile(requestedFile, destFile);
                        } catch (Exception ioe) {
                            logger.severe("An error occurred while attempting to copy file: ["+ioe.getClass().getName() +"] "+ ioe.getMessage());
                            success = false;
                        }

                        if (success) {
                            return mapping.findForward("success");
                        } else {
                            request.setAttribute("message", "cannot copy that file to that location");
                            response.setStatus(HttpServletResponse.SC_CONFLICT);

                            if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                                return mapping.findForward("error");
                            } else {
                                return mapping.findForward("error-txt");
                            }

                        }
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

                request.setAttribute("message", "copy must be performed via a GET operation, and required params must be specified");
                response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                    return mapping.findForward("error");
                } else {
                    return mapping.findForward("error-txt");
                }

            }

        } catch (Exception e) {

            logger.severe("An error occurred while attempting to copy file: ["+e.getClass().getName() +"] "+ e.getMessage());
            request.setAttribute("message", "An error occurred while attempting to copy file: ["+e.getClass().getName() +"] "+ e.getMessage());
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);

            if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                return mapping.findForward("error");
            } else {
                return mapping.findForward("error-txt");
            }


        }

    }

    // Copies src file to dst file.
    // If the dst file does not exist, it is created
    // can I just ask why java doesn't have an actual method for doing this natively?
    public static void copyFile(File src, File dst) throws Exception {
        String from, to;
        from = src.getAbsolutePath();
        to = dst.getAbsolutePath();

        String[] command = {"cp","-R",from,to};

        Runtime.getRuntime().exec(command);
        logger.info("cp -R '"+from+"' '"+to+"'");
    }


}
