package au.edu.murdoch.ccg.yabi.actions;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;

import java.util.*;

public class JBPMDelay extends BaseAction {

  public void execute(ExecutionContext ctx) throws Exception {
    Map myVars = varTranslator.getVariableMap(ctx);
    Map inputVars = (Map) myVars.get("input");
    Map outputVars = (Map) myVars.get("output");

  	varTranslator.saveVariable(ctx, "processingVar", "true");
  
  	varTranslator.saveVariable(ctx, "param", inputVars.get("param 1"));

	//sleep 'delay' seconds or default to 20
    int delay = 20000;
    try {
         delay = Integer.parseInt( (String) inputVars.get("delay") );
    } catch (Exception e) {}
	Thread.sleep(delay); 
    
    varTranslator.saveVariable(ctx, "processingVar", "false");
    
    // graph execution propagation
    ctx.leaveNode("next");
  }

}
