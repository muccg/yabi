package au.edu.murdoch.ccg.yabi.actions;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;

import au.edu.murdoch.ccg.yabi.util.GenericProcessingClient;
import au.edu.murdoch.ccg.yabi.util.ProcessingClientFactory;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.objects.YabiJobFileInstance;
import org.apache.commons.configuration.*;

import java.util.*;
import java.text.SimpleDateFormat;
import java.io.File;
import au.edu.murdoch.ccg.yabi.util.SymLink;

public class CleanupAction extends BaseAction {

  public void execute(ExecutionContext ctx) throws Exception {
    Map myVars = varTranslator.getVariableMap(ctx);
    Map inputVars = (Map) myVars.get("input");
    Map outputVars = (Map) myVars.get("output");

    String jobName = varTranslator.getProcessVariable(ctx, "jobName");
    String year = varTranslator.getProcessVariable(ctx, "year");
    String month = varTranslator.getProcessVariable(ctx, "month");
    String userName = varTranslator.getProcessVariable(ctx, "username");

    boolean result = this.moveSymLink(userName, year, month, jobName);

    if (result) {
        varTranslator.saveVariable(ctx, "jobStatus", "C");
    } else {
        varTranslator.saveVariable(ctx, "errorMessage", "error moving process from running to completed status");
        varTranslator.saveVariable(ctx, "jobStatus", "E");
    }

    //locate the jobxml file
    String jobFile = varTranslator.getProcessVariable(ctx, "jobXMLFile");

    //output the endtime into the jobXML file
    YabiJobFileInstance yjfi = new YabiJobFileInstance(jobFile);
    yjfi.setEndTime( new SimpleDateFormat("EEE, d MMM yyyy HH:mm:ss").format( new java.util.Date() ) );
    //also make sure all process variables are dumped, such as errors etc
    Map vars = ctx.getProcessInstance().getContextInstance().getVariables();
    yjfi.insertVariableMap(vars);
    yjfi.saveFile();


    ctx.getContextInstance().setVariable("jobStatus", "completed");
    ctx.leaveNode("next");
  }

    private boolean moveSymLink(String username, String year, String month, String jobName) throws Exception {
        Configuration conf = YabiConfiguration.getConfig();
        String rootDir = conf.getString("yabi.rootDirectory");
         
        jobName = jobName.replaceAll(" ", "_");
       
        String from = rootDir + username + "/.running/" + jobName;
        String to = rootDir + username + "/.completed";
        String linkTo = rootDir + username + "/jobs/" + year + "-" + month + "/" + jobName;

        File old = new File(from);
        boolean res = old.delete();
        System.out.println("deleted file ["+from+"]");

        SymLink.createSymLink(linkTo, to);

        if (!res) return false; //return false if we failed to delete the .running link, just so there is an error code to be seen
        return true;
    }       

}
