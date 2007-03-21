package au.edu.murdoch.ccg.yabi.actions;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;

import au.edu.murdoch.ccg.yabi.util.GenericProcessingClient;
import au.edu.murdoch.ccg.yabi.util.ProcessingClientFactory;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.objects.YabiJobFileInstance;
import org.apache.commons.configuration.*;

import java.util.*;

public class WaitForJobAction extends BaseAction {

  private int waitTime = 1000; // start at 1 second
  private int maxWaitTime = 30000; //max wait time of 30 sec
  private String grendelHost;

  public void execute(ExecutionContext ctx) throws Exception {
    Map myVars = varTranslator.getVariableMap(ctx);
    Map inputVars = (Map) myVars.get("input");
    Map outputVars = (Map) myVars.get("output");

    //validate that we have the jobId that we require
    if (inputVars.get("jobId") != null) {

        boolean isCompleted = false;

        try {
            String nodeName = ctx.getNode().getFullyQualifiedName();

            GenericProcessingClient pclient = ProcessingClientFactory.createProcessingClient( (String) inputVars.get("jobType") , null );

            while ( ! isCompleted ) {
  
                //write the actual status string to the output 
                String status = pclient.getJobStatus( (String) inputVars.get("jobId") );
                varTranslator.saveVariable(ctx, "jobStatus", status );

                //locate the jobxml file
                String jobFile = varTranslator.getProcessVariable(ctx, "jobXMLFile");
                Configuration conf = YabiConfiguration.getConfig();

                //dump the variables for this node into the jobXML file
                YabiJobFileInstance yjfi = new YabiJobFileInstance(jobFile);
                Map vars = ctx.getProcessInstance().getContextInstance().getVariables();
                yjfi.insertVariableMap(vars);
                yjfi.saveFile();

                //completed
                if (pclient.isCompleted()) {
                    isCompleted = true;

                    // ----- STAGE OUT FILES -----
                    //get the outputdir
                    String outputDir = varTranslator.getProcessVariable(ctx, "jobDataDir");
                    pclient.setOutputDir(outputDir);
                    String tmpName = nodeName.replaceAll("-check","");
                    pclient.setStageOutPrefix(tmpName);
                    pclient.fileStageOut( null );
                }

                //error
                if (pclient.hasError()) {
                    isCompleted = true;
                    varTranslator.saveVariable(ctx, "errorMessage", "processing server error");
                    ctx.leaveNode("error");
                }

                if (! pclient.isCompleted()) {
                    try {
                        System.out.println("[WaitForJobAction] backing off for "+waitTime+" ms");
                        Thread.sleep(waitTime);
                        waitTime += waitTime;  //exponential backoff
                        if (waitTime > maxWaitTime) {
                            waitTime = maxWaitTime;
                        }
                    } catch (InterruptedException e) {}
                }

            }
        } catch (Exception e) {

            varTranslator.saveVariable(ctx, "errorMessage", e.getClass() + " : " + e.getMessage());
            //propagate execution to error state
            ctx.leaveNode("error");

        }

    } else {

        varTranslator.saveVariable(ctx, "errorMessage", "Missing input variable: jobId");
        ctx.leaveNode("error");
 
    }

    //do not propagate execution. wait for grendel return
    
  }

}
