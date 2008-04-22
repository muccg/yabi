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

public class PreviewUserspaceFile extends BaseAction {

    private static Logger logger;

    public PreviewUserspaceFile () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        logger = Logger.getLogger( AppDetails.getAppString( request.getContextPath() ) + "." + PreviewUserspaceFile.class.getName() );
        String outputFormat = request.getParameter("outputformat");

        try {

            Configuration conf = YabiConfiguration.getConfig();
            String rootDirLoc = conf.getString("yabi.rootDirectory");

            //method should be a GET
            if (request.getMethod().compareTo("GET") == 0 &&
                request.getParameter("user") != null &&
                request.getParameter("file") != null ) {

                String user = request.getParameter("user").replaceAll("\\.\\.","");
                String relPath = request.getParameter("file").replaceAll("\\.\\.","");

                String filePath = rootDirLoc + user + "/" + relPath;
                File requestedFile = new File(filePath);
                
                String extension;

                //make sure the filename has an extension, so we can work with it
                if ( relPath.lastIndexOf(".") == -1 || relPath.lastIndexOf(".") == relPath.length() - 1 ) {
                    extension = "";
                } else {
                    extension = relPath.substring( relPath.lastIndexOf(".") + 1 );
                }


                if (requestedFile.exists()) {

                    request.setAttribute("file", requestedFile);

                    //default preview for any non-binary file
                    if (extension.compareTo("zip") != 0 &&
                        extension.compareTo("ab1") != 0 &&
                        extension.compareTo("jpg") != 0 &&
                        extension.compareTo("gif") != 0 &&
                        extension.compareTo("tar") != 0 &&
                        extension.compareTo("gz") != 0) {
                        String output = "";
                        FileReader fr = new FileReader(filePath);
                        char[] buf = new char[2500];
                        int charCount = fr.read(buf, 0, 2500);
                        fr.close();
                        if (charCount > 0) output = String.valueOf(buf, 0, charCount);

                        if (output.length() == 2500) {
                            output += " ...[file truncated for preview]";
                        }

                        request.setAttribute("preview", output);
                    } else {
                        request.setAttribute("preview", "no preview available for this filetype");
                    }

                    return mapping.findForward("success");

                } else {
                    
                    request.setAttribute("message", "requested file does not exist");
                    response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                    if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                        return mapping.findForward("error");
                    } else {
                        return mapping.findForward("error-txt");
                    }
                }

            } else {

                request.setAttribute("message", "download must be performed via a GET operation, and required params must be specified");
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
