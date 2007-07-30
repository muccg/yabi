package au.edu.murdoch.ccg.yabi.actions;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;

import au.edu.murdoch.ccg.yabi.util.ProcessingClientFactory;
import au.edu.murdoch.ccg.yabi.util.GenericProcessingClient;
import au.edu.murdoch.ccg.yabi.util.FileParamExpander;
import au.edu.murdoch.ccg.yabi.objects.BaatInstance;
import java.util.*;


public class SubmitJobAction extends BaseAction {

  public void execute(ExecutionContext ctx) throws Exception {
    Map myVars = varTranslator.getVariableMap(ctx);
    Map inputVars = (Map) myVars.get("input");
    Map outputVars = (Map) myVars.get("output");
    String username = varTranslator.getProcessVariable(ctx, "username");

    //check for presence of required inputs
    if ( inputVars.get("toolName") != null ) {

        //we get the toolname
        //all the rest are parameters, but we package them into a BaatInstance object so that
        //we can easily get the list of inputfiles and output files based on the baat xml info

        try {
            ArrayList totalOutputFiles = new ArrayList();
            String allJobIds = "";       
            String batchParam = null;
            String[] batchIterations = "".split(",");
            String inputFileTypes = null;

            // --- for batch jobs, create an arraylist with the substitutions ---
            if ( inputVars.get("batchOnParameter") != null && inputVars.get("batchOnParameter") instanceof String ) {
                batchParam = (String) inputVars.get("batchOnParameter");

                FileParamExpander fpe = new FileParamExpander();
                fpe.setUsername(username);

                //filtering based on 'inputFileTypes' param if it exists
                if ( inputVars.get("inputFiletypes") != null && inputVars.get("inputFiletypes") instanceof String ) {
                    inputFileTypes = (String) inputVars.get("inputFiletypes");
                    fpe.setFilter(inputFileTypes);
                }

                batchIterations = fpe.expandString( (String) inputVars.get(batchParam) );
                inputVars.remove("batchOnParameter");
            }

            for (int i = 0; i < batchIterations.length; i++) {
                BaatInstance bi = new BaatInstance( (String) inputVars.get("toolName") ); //this will throw an exception if toolName not found
                //now we process each input parameter and insert it as a parameter to the BaatInstance
                //this gives us a chance to filter the vars based on name, and inserting them into BaatInstance fetches inputFiles and outputFiles
                Iterator iter = inputVars.keySet().iterator(); 
                while (iter.hasNext()) {
                    String keyName = (String) iter.next();
                    String value = (String) inputVars.get(keyName);

                    //perform substitution if we are doing a batch version
                    if (batchParam != null && batchParam.compareTo(keyName) == 0) {
                        value = batchIterations[i];
                    }

                    bi.setParameter(keyName, value);
                }

                // ----- CREATE CLIENT -----
                GenericProcessingClient pclient = ProcessingClientFactory.createProcessingClient( (String) inputVars.get("jobType")  , bi);
                String outputDir = varTranslator.getProcessVariable(ctx, "jobDataDir");
                pclient.setOutputDir(outputDir);
                pclient.setInputDirByUsername(username);
                String nodeName = ctx.getNode().getFullyQualifiedName();
                pclient.setStageOutPrefix(nodeName);

                // ----- AUTHENTICATE -----
                pclient.authenticate( null );

                // ----- STAGE IN FILES ----- 
                pclient.fileStageIn( bi.getInputFiles() );
                ArrayList outputFiles = bi.getOutputFiles();
                totalOutputFiles.addAll(outputFiles);

                // ----- SUBMIT JOB -----
                long jobId = pclient.submitJob();
                //batch append jobId
                if (allJobIds.length() > 0) {
                    allJobIds += ","+jobId;
                } else {
                    allJobIds = ""+jobId;
                }
            }

            // --- for batch jobs, rejoin here ---

            varTranslator.saveVariable(ctx, "expectedOutputFiles", ""+totalOutputFiles);
            varTranslator.saveVariable(ctx, "jobId", allJobIds);
            //output dir variable
            String outputDir = varTranslator.getProcessVariable(ctx, "jobDataDir") + "/" + ctx.getNode().getFullyQualifiedName();
            outputDir = outputDir.substring( username.length() + 1 ); //strip username/ from the beginning
            varTranslator.saveVariable(ctx, "dir", outputDir);

        } catch (Exception e) {
            varTranslator.saveVariable(ctx, "errorMessage", e.getClass().getName() + " : " + e.getMessage());
            varTranslator.saveVariable(ctx, "jobStatus", "E" );

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
