package au.edu.murdoch.ccg.yabi.actions;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;

import au.edu.murdoch.ccg.yabi.util.GenericProcessingClient;
import au.edu.murdoch.ccg.yabi.util.ProcessingClientFactory;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.util.AppDetails;
import au.edu.murdoch.ccg.yabi.objects.YabiJobFileInstance;
import au.edu.murdoch.ccg.yabi.objects.BaatInstance;
import au.edu.murdoch.ccg.yabi.util.MailTool;
import org.apache.commons.configuration.*;
import au.edu.murdoch.cbbc.util.*;
import au.edu.murdoch.ccg.yabi.objects.User;


import java.util.*;

import java.util.logging.Logger;

public class WaitForJobAction extends BaseAction {

  private int waitTime = 1000; // start at 1 second
  private int maxWaitTime = 30000; //max wait time of 30 sec
  private static Logger logger = Logger.getLogger( AppDetails.getAppString() + "." + WaitForJobAction.class.getName());

  public void execute(ExecutionContext ctx) throws Exception {
    Map myVars = varTranslator.getVariableMap(ctx);
    Map inputVars = (Map) myVars.get("input");
    Map outputVars = (Map) myVars.get("output");
    String username = varTranslator.getProcessVariable(ctx, "username");


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

            BaatInstance bi = new BaatInstance( (String) inputVars.get("toolName") );

            //if jobType doesn't exist, then it will load the baat default. we are going to write this into variables so the fact is revealed to any clients
            if (inputVars.get("jobType") == null || ((String) inputVars.get("jobType")).compareTo("") == 0) {
                ctx.getContextInstance().setVariable( ctx.getNode().getFullyQualifiedName() + ".input.jobType" , bi.getJobType());
                inputVars.put("jobType", bi.getJobType());
            } 

            GenericProcessingClient pclient = ProcessingClientFactory.createProcessingClient( (String) inputVars.get("jobType") , bi );
            // ----- AUTHENTICATE -----
            pclient.authenticate( new User(username) );

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
                        
                        //display progress in the subJobsCompleted field
                        varTranslator.saveVariable(ctx, "subJobsCompleted", ""+(jobId.length - incompleteCount));

                        // ----- STAGE OUT FILES -----
                        //get the outputdir
                        String outputDir = varTranslator.getProcessVariable(ctx, "jobDataDir");
                        pclient.setBatchId( i + 1, jobId.length); //inform the client which iteration out of how many 
                        pclient.setOutputDir(outputDir);
                        String tmpName = nodeName.replaceAll("-check","");
                        pclient.setStageOutPrefix(tmpName);
                        pclient.fileStageOut( null );
                        
                        // ----- RUN ASSERTIONS -----
                        //throws an Exception if any assertions fail
                        pclient.runAssertions();
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
                        logger.fine("[WaitForJobAction] backing off for "+waitTime+" ms, incomplete batch items: "+incompleteCount);
                        Thread.sleep(waitTime);
                        waitTime += waitTime;  //exponential backoff
                        if (waitTime > maxWaitTime) {
                            waitTime = maxWaitTime;
                        }
                    } catch (InterruptedException e) {}
                }

            } //endfor
        } catch (Exception e) {

            try {
                MailTool mt = new MailTool();
                mt.sendYabiError(e.getClass().getName() + " : " + e.getMessage() + "\n\n" + MailTool.trapStackTrace(e));
            } catch (Exception cbbce) {}
            
            varTranslator.saveVariable(ctx, "errorMessage", e.getClass() + " : " + e.getMessage());
            varTranslator.saveVariable(ctx, "jobStatus", "E" );
            //propagate execution to error state
            varTranslator.updateLastNodeMarker(ctx);
            ctx.leaveNode("error"); //TODO change this so it just cancels checking this node

        }


    } else {

        try {
            MailTool mt = new MailTool();
            mt.sendYabiError("Missing input variable: jobId");
        } catch (Exception cbbce) {}
        
        varTranslator.saveVariable(ctx, "errorMessage", "Missing input variable: jobId");
        varTranslator.updateLastNodeMarker(ctx);
        ctx.leaveNode("error");
 
    }

    //do not propagate execution. wait for return
    varTranslator.updateLastNodeMarker(ctx);
  }

}
