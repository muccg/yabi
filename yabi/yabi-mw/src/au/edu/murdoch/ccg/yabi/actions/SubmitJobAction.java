package au.edu.murdoch.ccg.yabi.actions;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;

import au.edu.murdoch.ccg.yabi.util.ProcessingClientFactory;
import au.edu.murdoch.ccg.yabi.util.GenericProcessingClient;
import au.edu.murdoch.ccg.yabi.util.FileParamExpander;
import au.edu.murdoch.ccg.yabi.util.SymLink;
import au.edu.murdoch.ccg.yabi.objects.BaatInstance;
import au.edu.murdoch.ccg.yabi.objects.YabiJobFileInstance;
import au.edu.murdoch.ccg.yabi.util.AppDetails;
import au.edu.murdoch.ccg.yabi.objects.User;

import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.util.MailTool;
import org.apache.commons.configuration.*;
import au.edu.murdoch.cbbc.util.*;

import java.util.*;

import java.util.logging.Logger;

public class SubmitJobAction extends BaseAction {

  private static Logger logger = Logger.getLogger(AppDetails.getAppString() + "." + SubmitJobAction.class.getName());

  public void execute(ExecutionContext ctx) throws Exception {
    Map myVars = varTranslator.getVariableMap(ctx);
    Map inputVars = (Map) myVars.get("input");
    Map outputVars = (Map) myVars.get("output");
    String username = varTranslator.getProcessVariable(ctx, "username");
    String checkStatus = (String) myVars.get("checkStatus");
    //if the node has already been run (in an earlier invocation, for example) then skip this node
    if (checkStatus.compareTo("C") == 0) {
        //an early return prompts a move to the next node, which is the 'check' node, which we will also skip
        return;
    }

    //check for presence of required inputs
    if ( inputVars.get("toolName") != null ) {

        //explicitly clear out the output variables for this node in case we are re-running and want to clear out
        //any old error messages and jobIds
        myVars = varTranslator.clearNodeOutputMap(ctx);
        inputVars = (Map) myVars.get("input");
        outputVars = (Map) myVars.get("output");

        //we get the toolname
        //all the rest are parameters, but we package them into a BaatInstance object so that
        //we can easily get the list of inputfiles and output files based on the baat xml info

        try {
            ArrayList totalOutputFiles = new ArrayList();
            String allJobIds = "";       
            String batchParam = null;
            String[] batchIterations = "".split(",");
            String inputFileTypes = null;
            String[] bundledFiles = "".split(","); //any files that we will send along just in case but aren't a parameter

            // --- for batch jobs, create an arraylist with the substitutions ---
            if ( inputVars.get("batchOnParameter") != null && inputVars.get("batchOnParameter") instanceof String ) {
                batchParam = (String) inputVars.get("batchOnParameter");

                FileParamExpander fpe = new FileParamExpander();
                fpe.setUsername(username);

                //filtering based on 'inputFileTypes' param if it exists
                if ( inputVars.get("inputFiletypes") != null && inputVars.get("inputFiletypes") instanceof String ) {
                    inputFileTypes = (String) inputVars.get("inputFiletypes");
                    fpe.setFilter(inputFileTypes);
                    //now load up the baat and see if we are overriding the generic tool inputFiletypes for
                    //a more specific filter on the parameter we are using to batch on
                    BaatInstance bi = new BaatInstance( (String) inputVars.get("toolName") ); //this will throw an exception if toolName not found
                    String paramFilter = bi.getPrimaryExtension(batchParam);
                    if (paramFilter != null) {
                        fpe.removeFilter(paramFilter);
                    }
                    bundledFiles = fpe.expandString( (String) inputVars.get(batchParam) );

                    fpe = new FileParamExpander();
                    fpe.setUsername(username);
                    if (paramFilter != null) {
                        inputFileTypes = paramFilter;
                    }

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

                    //special parameters
                    if (keyName.compareTo("blastAddToSOE") == 0) {
                        bi.setGrendelOption("eric", value);
                        continue; //proceed to next variable
                    }

                    //perform substitution if we are doing a batch version
                    if (batchParam != null && batchParam.compareTo(keyName) == 0) {
                        value = batchIterations[i];
                    }

                    bi.setParameter(keyName, value);
                }

                bi.setUsername(username);

                // ----- CREATE CLIENT -----
                GenericProcessingClient pclient = ProcessingClientFactory.createProcessingClient( (String) inputVars.get("jobType")  , bi);
                String outputDir = varTranslator.getProcessVariable(ctx, "jobDataDir");
                pclient.setOutputDir(outputDir);
                pclient.setInputDirByUsername(username);
                String nodeName = ctx.getNode().getFullyQualifiedName();
                pclient.setStageOutPrefix(nodeName);
                //if required, symlink output dir to whatever the last executed node's directory is
                //provided that there is a last node
                if (bi.getSymlinkOutputDir() && varTranslator.getLastNodeMarker(ctx).length() > 0) {
                    try {
                        Configuration conf = YabiConfiguration.getConfig();
                        String rootDir = conf.getString("yabi.rootDirectory");

                        pclient.setStageOutPrefix(varTranslator.getLastNodeMarker(ctx));
                        SymLink.createSymLink( rootDir + outputDir + "/" + varTranslator.getLastNodeMarker(ctx), rootDir + outputDir + "/" + ctx.getNode().getFullyQualifiedName() );
                    } catch (Exception e) {
                        logger.severe("error creating symlink: "+e.getMessage());
                    }
                }

                // ----- AUTHENTICATE -----
                pclient.authenticate( new User(username) );

                // ----- STAGE IN FILES ----- 
                bi.addInputFiles(bundledFiles);
                logger.fine("batch item ["+batchIterations[i]+"] bundling ["+bi.getInputFiles()+"]");
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

            try {
                MailTool mt = new MailTool();
                mt.sendYabiError(username+" encountered:\n\n"+e.getClass().getName() + " : " + e.getMessage() + "\n\n" + MailTool.trapStackTrace(e));
            } catch (Exception cbbce) {}
            
            //propagate execution to error state
            ctx.leaveNode("error");
        }

    } else {
        varTranslator.saveVariable(ctx, "errorMessage", "Missing input : toolName");
        ctx.leaveNode("error");
    }

    //locate the jobxml file
    String jobFile = varTranslator.getProcessVariable(ctx, "jobXMLFile");

    //dump the variables for this node into the jobXML file
    YabiJobFileInstance yjfi = new YabiJobFileInstance(jobFile);
    Map vars = ctx.getProcessInstance().getContextInstance().getVariables();
    yjfi.insertVariableMap(vars);
    yjfi.saveFile();

    //proceed to next node
    
  }

}
