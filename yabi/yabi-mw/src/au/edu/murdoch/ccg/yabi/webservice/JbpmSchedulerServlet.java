package au.edu.murdoch.ccg.yabi.webservice;

import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.jbpm.scheduler.impl.*;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.jbpm.JbpmConfiguration;
import org.jbpm.JbpmContext;

import au.edu.murdoch.ccg.yabi.jbpm.SchedulerThread;

/**
 * JbpmSchedulerServlet
 * this class is required (rather than using a default JBPM servlet) in order to provide
 * a custom configuration to a servlet that terminates properly when we redeploy the webapp
 * something that the Jbpm default servlets do not do well at all
 **/
public class JbpmSchedulerServlet extends HttpServlet {

  private static final long serialVersionUID = 1L;
 
  String jbpmConfigurationResource = null;
  String jbpmContextName = null; 
  SchedulerThread schedulerThread = null;

  public void init() throws ServletException {
    // get the jbpm configuration resource
    this.jbpmConfigurationResource = getInitParameter("jbpm.configuration.resource");
    
    if (jbpmConfigurationResource==null) {
      log.debug("using default jbpm cfg resource");
    } else {
      log.debug("using jbpm cfg resource: '"+jbpmConfigurationResource+"'");
    }

    // get the jbpm context to be used from the jbpm configuration
    this.jbpmContextName = getInitParameter("jbpm.context.name");

    if (jbpmContextName==null) {
      log.debug("using default jbpm context");
      jbpmContextName = JbpmContext.DEFAULT_JBPM_CONTEXT_NAME;
    } else {
      log.debug("using jbpm context: '"+jbpmContextName+"'");
    }

    JbpmConfiguration jbpmConfiguration = JbpmConfiguration.getInstance(jbpmConfigurationResource);

    schedulerThread = new SchedulerThread(jbpmConfiguration);
    schedulerThread.start();
  }
  
  public void destroy() {
    stopSchedulerThread();
  }

  public void stopSchedulerThread() {
    if (isRunning()) {
      log.debug("stopping the scheduler");
      schedulerThread.setKeepRunning(false);
      schedulerThread.interrupt();
      schedulerThread = null;
    } else {
      log.debug("scheduler can't be stopped cause it was not running");
    }
  }
  
  public boolean isRunning() {
    return ( (schedulerThread!=null)
             && (schedulerThread.isAlive()) );
  }

  protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
    PrintWriter out = response.getWriter();
    out.println("<html>");
    out.println("<body>");
    out.println("<h2>jBPM Scheduler Servlet</h2><hr />");
    out.println("</body>");
    out.println("</html>");
  }

  String getInitParameter(String name, String defaultValue) {
    String value = getInitParameter(name);
    if (value!=null) {
      return value;
    }
    return defaultValue;
  }

  private static Log log = LogFactory.getLog(JbpmSchedulerServlet.class);
}
