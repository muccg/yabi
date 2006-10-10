package au.edu.murdoch.ccg.yabi.actions;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;

import au.edu.murdoch.ccg.yabi.util.GrendelClient;
import java.util.*;

public class WaitForGrendelXMLJobAction extends BaseAction {

  private int waitTime = 30000; // 30 seconds
  private String grendelHost = "http://carah.localdomain:8080";
  private String jobsDir = "/jobs";

  public void execute(ExecutionContext ctx) throws Exception {
    Map myVars = varTranslator.getVariableMap(ctx);
    Map inputVars = (Map) myVars.get("input");
    Map outputVars = (Map) myVars.get("output");

    //validate that we have the jobId that we require
    if (inputVars.get("jobId") != null) {

        boolean isCompleted = false;

        try {

            GrendelClient gc = new GrendelClient();

            while ( ! isCompleted ) {
   
                String status = gc.getJobStatus( (String) inputVars.get("jobId") );
                varTranslator.saveVariable(ctx, "jobStatus", status );

                //completed
                if (status.compareTo("C") == 0) {
                    isCompleted = true;
                    varTranslator.saveVariable(ctx, "resultsFile", generateResultLocation( (String) inputVars.get("jobId") ) );

                    // ----- STAGE OUT FILES -----
                    //TODO
                    //TODO grab results file and unzip to a predictable location
                }

                //error
                if (status.compareTo("E") == 0) {
                    isCompleted = true;
                    varTranslator.saveVariable(ctx, "errorMessage", "grendel error");
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
    String result = grendelHost + jobsDir + "/" + dirName + "/" + jobId + ".zip";

    return result;
  }

}
