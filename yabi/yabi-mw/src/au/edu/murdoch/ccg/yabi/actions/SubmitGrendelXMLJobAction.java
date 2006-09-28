package au.edu.murdoch.ccg.yabi.actions;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;

import au.edu.murdoch.ccg.yabi.util.GrendelClient;
import java.util.*;

public class SubmitGrendelXMLJobAction extends BaseAction {

  public void execute(ExecutionContext ctx) throws Exception {
    Map myVars = varTranslator.getVariableMap(ctx);
    Map inputVars = (Map) myVars.get("input");
    Map outputVars = (Map) myVars.get("output");

    //check for presence of required inputs
    if ( inputVars.get("jobXML") != null ) {

        try {
            String[] attachment = null;
            if ( inputVars.get("attachment") != null ) {
                attachment = new String[1];
                attachment[0] = (String) inputVars.get("attachment");
            }
            long jobId = GrendelClient.submitXMLJob( (String) inputVars.get("jobXML") , attachment);
            varTranslator.saveVariable(ctx, "jobId", ""+jobId);
        } catch (Exception e) {
            varTranslator.saveVariable(ctx, "errorMessage", e.getMessage());

            //propagate execution to error state
            ctx.leaveNode("error");
        }

    } else {
        varTranslator.saveVariable(ctx, "errorMessage", "Missing input : jobXML");
        ctx.leaveNode("error");
    }

    //do not propagate execution. wait for grendel return
    
  }

}
