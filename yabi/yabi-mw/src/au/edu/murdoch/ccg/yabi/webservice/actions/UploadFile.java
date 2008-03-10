package au.edu.murdoch.ccg.yabi.webservice.actions;

import java.util.*;
import java.io.*;
import java.text.SimpleDateFormat;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

import au.edu.murdoch.ccg.yabi.objects.YabiJobFileInstance;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.util.SymLink;
import au.edu.murdoch.ccg.yabi.util.AppDetails;

import org.apache.commons.configuration.*;
import org.apache.commons.fileupload.servlet.ServletFileUpload;
import org.apache.commons.fileupload.disk.*;
import org.apache.commons.fileupload.*;

import java.util.logging.Logger;

public class UploadFile extends BaseAction {

    private static Logger logger;

    public UploadFile () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        logger = Logger.getLogger( AppDetails.getAppString( request.getContextPath() ) + "." + UploadFile.class.getName() );
        String outputFormat = request.getParameter("outputformat");

        try {

            Configuration conf = YabiConfiguration.getConfig();
            String rootDirLoc = conf.getString("yabi.rootDirectory");
            String tempDirLoc = rootDirLoc + "/uploadTemp";
            File tempDir = new File(tempDirLoc);
            if (!tempDir.exists()) {
                tempDir.mkdirs();
            }
    
            //method should be a POST
            if (request.getMethod().compareTo("POST") == 0) {

                boolean isMultipart = ServletFileUpload.isMultipartContent(request);

                if (isMultipart) {
                    // Create a factory for disk-based file items
                    DiskFileItemFactory factory = new DiskFileItemFactory();

                    // Set factory constraints
                    factory.setSizeThreshold(1);
                    factory.setRepository(tempDir);

                    // Create a new file upload handler
                    ServletFileUpload upload = new ServletFileUpload(factory);

                    // Set overall request size constraint
                    upload.setFileSizeMax(8L * 1024L * 1024L * 500L); //500MB

                    // Parse the request
                    List /* FileItem */ items = upload.parseRequest(request);

                    List files = new ArrayList();
                    String username = "";

                    // Process the uploaded items
                    Iterator iter = items.iterator();
                    while (iter.hasNext()) {
                        FileItem item = (FileItem) iter.next();

                        if (item.isFormField()) {
                            if (item.getFieldName().compareTo("user") == 0) {
                                username = item.getString();
                            }
                        } else {
                            files.add(item);
                        }
                    }

                    if (username.length() > 1 && username.indexOf("..") < 0) {
                        String outputPath = rootDirLoc + username + "/workspace/";
                        File outputDir = new File(outputPath);
                        if (!outputDir.exists()) {
                            //outputDir.mkdirs();
                            request.setAttribute("message", "User workspace does not exist, please login to YABI front-end to create it");
                            response.setStatus(HttpServletResponse.SC_CONFLICT);

                            if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                                return mapping.findForward("error");
                            } else {
                                response.setContentType("text/plain");
                                return mapping.findForward("error-txt");
                            }

                        }

                        Iterator fileIter = files.iterator();
                        while (fileIter.hasNext()) {
                            FileItem item = (FileItem) fileIter.next();

                            String outputFileLoc = outputPath + item.getName();
                            File outputFile = new File(outputFileLoc);
                            item.write(outputFile);
                            request.setAttribute("message", "Uploaded file: "+outputFileLoc);
                        }
                    } else {
                        request.setAttribute("message", "File upload must be identified by a username");
                        response.setStatus(HttpServletResponse.SC_BAD_REQUEST);

                        if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                            return mapping.findForward("error");
                        } else {
                            response.setContentType("text/plain");
                            return mapping.findForward("error-txt");
                        }

                    }
                } else {
                    request.setAttribute("message", "File upload must be performed via a multipart POST operation");
                    response.setStatus(HttpServletResponse.SC_BAD_REQUEST);

                    if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                        return mapping.findForward("error");
                    } else {
                        response.setContentType("text/plain");
                        return mapping.findForward("error-txt");
                    }

                }

                logger.info("file upload ismultipart: "+isMultipart);

            } else {
                request.setAttribute("message", "File upload must be performed via a POST operation");

                response.setStatus(HttpServletResponse.SC_BAD_REQUEST);

                if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                    return mapping.findForward("error");
                } else {
                    response.setContentType("text/plain");
                    return mapping.findForward("error-txt");
                }

            }

        } catch (Exception e) {

            logger.severe("An error occurred while attempting to upload file: ["+e.getClass().getName() +"] "+ e.getMessage());
            request.setAttribute("message", "An error occurred while attempting to upload file: ["+e.getClass().getName() +"] "+ e.getMessage());

            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);

            if (outputFormat == null || outputFormat.compareTo(TYPE_TXT) != 0) {
                return mapping.findForward("error");
            } else {
                response.setContentType("text/plain");
                return mapping.findForward("error-txt");
            }


        }

        return mapping.findForward("success");

    }

}
