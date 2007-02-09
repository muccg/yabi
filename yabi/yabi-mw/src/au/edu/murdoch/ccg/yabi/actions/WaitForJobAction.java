package au.edu.murdoch.ccg.yabi.actions;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;

import au.edu.murdoch.ccg.yabi.util.GenericProcessingClient;
import au.edu.murdoch.ccg.yabi.util.ProcessingClientFactory;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.objects.YabiJobFileInstance;
import org.apache.commons.configuration.*;

import java.util.*;

public class CleanupAction extends BaseAction {

    public void execute(ExecutionContext ctx) throws Exception {
        try {
            Map myVars = varTranslator.getVariableMap(ctx);
            Map inputVars = (Map) myVars.get("input");
            Map outputVars = (Map) myVars.get("output");

            //move the symlink from running to completed directory
            String jobFile = varTranslator.getProcessVariable(ctx, "jobXMLFile");
            Configuration conf = YabiConfiguration.getConfig();

            //dump the variables for this node into the jobXML file
            YabiJobFileInstance yjfi = new YabiJobFileInstance(jobFile);
            //yjfi.saveFile();

        } catch (Exception e) {

            varTranslator.saveVariable(ctx, "errorMessage", e.getClass() + " : " + e.getMessage());
            //propagate execution to error state
            ctx.leaveNode("error");

        }

        //do not propagate execution. wait for grendel return
    
    }

}
