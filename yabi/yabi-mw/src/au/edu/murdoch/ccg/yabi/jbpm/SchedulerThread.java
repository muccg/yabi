package au.edu.murdoch.ccg.yabi.jbpm;

import org.jbpm.scheduler.impl.*;
import org.jbpm.JbpmConfiguration;
import org.jbpm.JbpmContext;

public class SchedulerThread extends org.jbpm.scheduler.impl.SchedulerThread {

    public boolean keepRunning = true;

    public SchedulerThread(JbpmConfiguration jbpmConfiguration) {
        super(jbpmConfiguration, JbpmContext.DEFAULT_JBPM_CONTEXT_NAME);
    }

    public SchedulerThread(String jbpmContextName) {
        super(JbpmConfiguration.getInstance(), jbpmContextName);
    }

    public void setKeepRunning(boolean input) {
        this.keepRunning = input;
    }

}
