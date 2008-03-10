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

public class DownloadFile extends BaseAction {

    private static Logger logger;

    public DownloadFile () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        logger = Logger.getLogger( AppDetails.getAppString( request.getContextPath() ) + "." + DownloadFile.class.getName() );
        String outputFormat = request.getParameter("outputformat");

        try {

            Configuration conf = YabiConfiguration.getConfig();
            String rootDirLoc = conf.getString("yabi.rootDirectory");

            //method should be a GET
            if (request.getMethod().compareTo("GET") == 0 &&
                request.getParameter("user") != null &&
                request.getParameter("year") != null &&
                request.getParameter("month") != null &&
                request.getParameter("jobname") != null &&
                request.getParameter("file") != null &&
                request.getParameter("node") != null) {

                //look for workflow file based on user, year, month and jobname
                String user = request.getParameter("user").replaceAll("\\.\\.","");
                String year = request.getParameter("year").replaceAll("[\\D]","");
                String month = request.getParameter("month").replaceAll("[\\D]","");
                String jobName = request.getParameter("jobname").replaceAll("\\.\\.","");
                String relPath = request.getParameter("file").replaceAll("\\.\\.","");
                String node = request.getParameter("node").replaceAll("\\.\\.","");

                String filePath = rootDirLoc + user + "/jobs/" + year + "-" + month + "/" + jobName + "/" + "/data/" + node + "/" + relPath;
                File requestedFile = new File(filePath);
                
                if (requestedFile.exists() && !requestedFile.isDirectory()) {

                    FileInputStream fileToDownload = new FileInputStream(filePath);
                    ServletOutputStream out = response.getOutputStream();

                    response.setContentType("application/download");
                    response.setHeader("Content-Disposition", "attachment; filename=" + requestedFile.getName());

                    int c;
                    while((c=fileToDownload.read()) != -1){
                    out.write(c);
                    }
                    out.flush();
                    out.close();
                    fileToDownload.close();
                    return null;

                } else {
                    
                    request.setAttribute("message", "requested file does not exist or is a directory");
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
