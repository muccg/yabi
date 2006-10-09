package au.edu.murdoch.ccg.yabi.actions;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;

import au.edu.murdoch.ccg.yabi.util.GrendelClient;
import au.edu.murdoch.ccg.yabi.objects.BaatInstance;
import au.edu.murdoch.ccg.yabi.util.Zipper;
import java.util.*;


public class SubmitGrendelXMLJobAction extends BaseAction {

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

            // ----- STAGE IN FILES ----- 
            //grab out arrayLists of inputFiles and outputFiles from the BaatInstance
            ArrayList inputFiles = bi.getInputFiles();
            ArrayList outputFiles = bi.getOutputFiles();

            //zip up all the input files and add the zipfile to the Baat
            String zipFileName = new Date().getTime() + ".zip";
            Zipper.createZipFile( zipFileName , "/tmp/", inputFiles );

            bi.setAttachedFile("file:///tmp/" + zipFileName);

            varTranslator.saveVariable(ctx, "expectedOutputFiles", ""+outputFiles);


            // ----- SUBMIT JOB -----
            long jobId = GrendelClient.submitXMLJob( bi.exportXML()  , bi.getAttachedFile() );
            varTranslator.saveVariable(ctx, "jobXML", bi.exportXML());
            //ctx.leaveNode("error");
            varTranslator.saveVariable(ctx, "jobId", ""+jobId);

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
