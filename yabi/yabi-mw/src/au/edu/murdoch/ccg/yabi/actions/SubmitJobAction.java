package au.edu.murdoch.ccg.yabi.actions;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;

import au.edu.murdoch.ccg.yabi.util.ProcessingClientFactory;
import au.edu.murdoch.ccg.yabi.util.GenericProcessingClient;
import au.edu.murdoch.ccg.yabi.objects.BaatInstance;
import java.util.*;


public class SubmitJobAction extends BaseAction {

  public void execute(ExecutionContext ctx) throws Exception {
    Map myVars = varTranslator.getVariableMap(ctx);
    Map inputVars = (Map) myVars.get("input");
    Map outputVars = (Map) myVars.get("output");

    //check for presence of required inputs
    if ( inputVars.get("toolName") != null ) {

        //we get the toolname
        //all the rest are parameters, but we package them into a BaatInstance object so that
        //we can easily get the list of inputfiles and output files based on the baat xml info

        try {
            BaatInstance bi = new BaatInstance( (String) inputVars.get("toolName") ); //this will throw an exception if toolName not found
        
            //now we process each input parameter and insert it as a parameter to the BaatInstance
            //this gives us a chance to filter the vars based on name, and inserting them into BaatInstance fetches inputFiles and outputFiles
            Iterator iter = inputVars.keySet().iterator(); 
            while (iter.hasNext()) {
                String keyName = (String) iter.next();
                String value = (String) inputVars.get(keyName);

                bi.setParameter(keyName, value);
            }

            // ----- CREATE CLIENT -----
            GenericProcessingClient pclient = ProcessingClientFactory.createProcessingClient( (String) inputVars.get("jobType")  , bi);

            // ----- AUTHENTICATE -----
            pclient.authenticate( null );

            // ----- STAGE IN FILES ----- 
            pclient.fileStageIn( bi.getInputFiles() );
            ArrayList outputFiles = bi.getOutputFiles();
            varTranslator.saveVariable(ctx, "expectedOutputFiles", ""+outputFiles);

            // ----- SUBMIT JOB -----
            long jobId = pclient.submitJob();
            varTranslator.saveVariable(ctx, "jobId", ""+jobId);

            // ----- STAGE OUT FILES -----

        } catch (Exception e) {
            varTranslator.saveVariable(ctx, "errorMessage", e.getClass().getName() + " : " + e.getMessage());

            e.printStackTrace();

            //propagate execution to error state
            ctx.leaveNode("error");
        }

    } else {
        varTranslator.saveVariable(ctx, "errorMessage", "Missing input : toolName");
        ctx.leaveNode("error");
    }

    //do not propagate execution. wait for grendel return
    
  }

}
