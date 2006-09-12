package au.edu.murdoch.ccg.yabi.actions;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;


public class JBPMDelay implements ActionHandler {
  public void execute(ExecutionContext ctx) throws Exception {
  	ctx.setVariable(ctx.getNode().getFullyQualifiedName() + ".processingVar", "true");
  
  	ctx.setVariable(ctx.getNode().getFullyQualifiedName() + ".inputParam", ctx.getVariable("input param 1"));

	//sleep 20 seconds
	Thread.sleep(20000); 
    
    ctx.setVariable(ctx.getNode().getFullyQualifiedName() + ".processingVar", "false");
    try {
		ctx.setVariable(ctx.getNode().getFullyQualifiedName() + ".transitionSource", ctx.getTransitionSource().getFullyQualifiedName());
	} catch (Exception e) {
		ctx.setVariable(ctx.getNode().getFullyQualifiedName() + ".transitionSource", "threw exception");
    }
    
    // graph execution propagation
    ctx.leaveNode("next");
  }
}
