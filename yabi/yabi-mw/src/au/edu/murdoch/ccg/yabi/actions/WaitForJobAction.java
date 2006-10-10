package au.edu.murdoch.ccg.yabi.actions;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;

import au.edu.murdoch.ccg.yabi.util.GenericProcessingClient;
import au.edu.murdoch.ccg.yabi.util.ProcessingClientFactory;
import java.util.*;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import org.apache.commons.configuration.*;

public class WaitForJobAction extends BaseAction {

  private int waitTime = 30000; // 30 seconds
  private String grendelHost;

  public void execute(ExecutionContext ctx) throws Exception {
    Map myVars = varTranslator.getVariableMap(ctx);
    Map inputVars = (Map) myVars.get("input");
    Map outputVars = (Map) myVars.get("output");

    //validate that we have the jobId that we require
    if (inputVars.get("jobId") != null) {

        boolean isCompleted = false;

        try {

            //load config data
            Configuration config = YabiConfiguration.getConfig();
            grendelHost = config.getString("grendel.resultsLocation");

            GenericProcessingClient pclient = ProcessingClientFactory.createProcessingClient( (String) inputVars.get("jobType") , null );

            while ( ! isCompleted ) {
  
                //write the actual status string to the output 
                String status = pclient.getJobStatus( (String) inputVars.get("jobId") );
                varTranslator.saveVariable(ctx, "jobStatus", status );

                //completed
                if (pclient.isCompleted()) {
                    isCompleted = true;
                    varTranslator.saveVariable(ctx, "resultsFile", generateResultLocation( (String) inputVars.get("jobId") ) );

                    // ----- STAGE OUT FILES -----
                    pclient.fileStageOut( null );
                }

                //error
                if (pclient.hasError()) {
                    isCompleted = true;
                    varTranslator.saveVariable(ctx, "errorMessage", "processing server error");
                    ctx.leaveNode("error");
                }

                try {
                    Thread.sleep(waitTime);
                } catch (InterruptedException e) {}

            }
        } catch (Exception e) {

            varTranslator.saveVariable(ctx, "errorMessage", e.getMessage());
            //propagate execution to error state
            ctx.leaveNode("error");

        }

    } else {

        varTranslator.saveVariable(ctx, "errorMessage", "Missing input variable: jobId");
        ctx.leaveNode("error");
 
    }

    //do not propagate execution. wait for grendel return
    
  }

  public String generateResultLocation(String jobId) {
    String dirName = jobId.substring(0,9);
    String result = grendelHost + "/" + dirName + "/" + jobId + ".zip";

    return result;
  }

}
