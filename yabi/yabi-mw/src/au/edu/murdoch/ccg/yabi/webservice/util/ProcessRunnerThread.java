package au.edu.murdoch.ccg.yabi.webservice.util;

import java.util.*;
import org.jbpm.graph.def.*;
import org.jbpm.graph.exe.*;
import org.jbpm.*;

public class ProcessRunnerThread extends Thread {

    private long processId = 0L;
    private JbpmConfiguration jbpmConfig;
    private boolean isDone = false;
    private int waitTime = 5000; //5 seconds before resignalling process

    public void setProcessId (long input) { this.processId = input; }
    public long getProcessId () { return this.processId; }
    public void setJbpmConfiguration (JbpmConfiguration input) { this.jbpmConfig = input; }

    public void run() {
        if (this.processId != 0L && this.jbpmConfig != null) {
     
            //we hound this process down until it is Ended or we hit an exception
            
            while (!isDone) {

                JbpmContext jbpm =  jbpmConfig.createJbpmContext();

                //first we load it up
                ProcessInstance pi = jbpm.getGraphSession().getProcessInstance( this.processId );

                //check status
                if (!pi.hasEnded()) {

                    //if it hasn't ended, signal it
                    pi.signal();

                    //now if it has ended, flag ourselves
                    if (pi.hasEnded()) {
                        isDone = true;
                    }
 
                } else {
                    isDone = true;
                }

                //close the jbpm session to save changes to DB
                jbpm.close();

                //sleep for a while
                try {
                    System.out.println("[ProcessRunnerThread]["+this.processId+"] done loop, sleeping now...");
                    Thread.sleep(waitTime);
                } catch (InterruptedException e) {
                    isDone = true;
                }
            }

        }

        System.out.println("[ProcessRunnerThread]["+this.processId+"] completed");
    }

}
