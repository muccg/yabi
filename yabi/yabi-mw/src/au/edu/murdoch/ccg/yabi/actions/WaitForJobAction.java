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

  public void execute(ExecutionContext ctx) throws Exception {
    Map myVars = varTranslator.getVariableMap(ctx);
    Map inputVars = (Map) myVars.get("input");
    Map outputVars = (Map) myVars.get("output");

    //if this node was already run and completed, then skip execution and fall through to next node
    String checkStatus = (String) outputVars.get("jobStatus");
    if (checkStatus != null && checkStatus.compareTo("C") == 0) {
        return;
    }

    //validate that we have the jobId that we require
    if (inputVars.get("jobId") != null) {

        //check if we are batched or not, depending on if jobId has commas
        String jobIdVar = (String)inputVars.get("jobId");
        boolean isBatched = false;
        String jobId[] = null;

        jobId = jobIdVar.split(",");

        boolean[] isCompleted = new boolean[jobId.length]; //used to track individual batch items
        int incompleteCount = jobId.length; //used to keep track of how many remain to be completed

        for (int i = 0; i < jobId.length; i++) {
            isCompleted[i] = false;
        }

        try {
            String nodeName = ctx.getNode().getFullyQualifiedName();

            GenericProcessingClient pclient = ProcessingClientFactory.createProcessingClient( (String) inputVars.get("jobType") , null );

            while ( incompleteCount > 0 ) {
      
                for (int i = 0; i < jobId.length; i++) {
                    //skip if already completed this iteration
                    if (isCompleted[i]) continue;

                    //write the actual status string to the output 
                    String status = pclient.getJobStatus( jobId[i] );
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
                        isCompleted[i] = true;
                        incompleteCount--;

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
                        isCompleted[i] = true;
                        incompleteCount--;

                        varTranslator.saveVariable(ctx, "errorMessage", "processing server error");
                        varTranslator.updateLastNodeMarker(ctx);
                        ctx.leaveNode("error"); //TODO change this so it doesn't drop out here, just cancels checking this node
                    }

                }

                if (incompleteCount > 0) {
                    try {
                        System.out.println("[WaitForJobAction] backing off for "+waitTime+" ms, incomplete batch items: "+incompleteCount);
                        Thread.sleep(waitTime);
                        waitTime += waitTime;  //exponential backoff
                        if (waitTime > maxWaitTime) {
                            waitTime = maxWaitTime;
                        }
                    } catch (InterruptedException e) {}
                }

            } //endfor
        } catch (Exception e) {

            varTranslator.saveVariable(ctx, "errorMessage", e.getClass() + " : " + e.getMessage());
            //propagate execution to error state
            varTranslator.updateLastNodeMarker(ctx);
            ctx.leaveNode("error"); //TODO change this so it just cancels checking this node

        }


    } else {

        varTranslator.saveVariable(ctx, "errorMessage", "Missing input variable: jobId");
        varTranslator.updateLastNodeMarker(ctx);
        ctx.leaveNode("error");
 
    }

    //do not propagate execution. wait for return
    varTranslator.updateLastNodeMarker(ctx);
  }

}
