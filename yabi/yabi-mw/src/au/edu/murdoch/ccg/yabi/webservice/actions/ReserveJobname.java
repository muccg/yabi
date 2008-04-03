package au.edu.murdoch.ccg.yabi.webservice.actions;

import org.jbpm.graph.def.*;
import org.jbpm.graph.exe.*;
import org.jbpm.*;
import java.util.*;
import java.io.*;
import java.text.SimpleDateFormat;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

import au.edu.murdoch.ccg.yabi.webservice.util.ProcessRunnerThread;
import au.edu.murdoch.ccg.yabi.objects.YabiJobFileInstance;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.util.SymLink;
import au.edu.murdoch.ccg.yabi.util.AppDetails;

import org.apache.commons.configuration.*;

import java.util.logging.Logger;

public class ReserveJobname extends BaseAction {

    private static Logger logger;
    private final Object lock = new Object();

    public ReserveJobname () {
        super();
    }

    public ActionForward execute(
        ActionMapping mapping,
        ActionForm form,
        HttpServletRequest request,
        HttpServletResponse response) throws Exception {

        logger = Logger.getLogger( AppDetails.getAppString( request.getContextPath() ) + "." + ReserveJobname.class.getName() );
 
        //method should be a POST
        if (request.getMethod().compareTo("POST") == 0) {

            String userName = request.getParameter("user");
            String year = request.getParameter("year");
            String month = request.getParameter("month");
            String jobName = request.getParameter("jobname");

            if (userName != null && userName.length() > 0 && 
                year != null && year.length() > 0 &&
                month != null && month.length() > 0 &&
                jobName != null && jobName.length() > 0) {

                //error out immediately if the workflow already exists
                boolean exists = false;

                synchronized (lock) {
                    YabiJobFileInstance yjfi = new YabiJobFileInstance();

                    File jobDir = new File(userName + "/jobs/" + year + "-" + month + "/" + jobName);
                    if (jobDir.exists()) {
                        exists = true;
                    }

                    //create jobdirs
                    jobDir.mkdirs();
                }

                //exit on already exists error
                if (exists) {
                    response.setStatus(HttpServletResponse.SC_CONFLICT);

                    logger.severe("A job directory of that name already exists");
                    request.setAttribute("message", "A job directory of that name already exists");
                    return mapping.findForward("error");
                }

                request.setAttribute("message", "/jobs/" + year + "-" + month + "/" + jobName);
                return mapping.findForward("success");

            } else {
                response.setStatus(HttpServletResponse.SC_BAD_REQUEST);

                request.setAttribute("message", "user, year, month and jobname must be specified");
                return mapping.findForward("error");
            }

        } else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);

            request.setAttribute("message", "Reserving jobname must be performed via a POST operation");
            return mapping.findForward("error");
        }

    }

}
