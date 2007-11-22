package au.edu.murdoch.ccg.yabi.objects;

import java.util.*;
import java.io.*;
import java.net.*;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.util.AppDetails;
import org.apache.commons.configuration.*;
import au.edu.murdoch.cbbc.util.CBBCException;

import java.util.logging.Logger;

public class RSLInstance {

    private String toolDirectory;
    
    private String toolName;
    private String rslContent;
    
    private static Logger logger = Logger.getLogger( AppDetails.getAppString() + "." + RSLInstance.class.getName());
    
    public RSLInstance (String toolName) throws Exception {
        //init vars
        this.toolName = toolName.replaceAll(System.getProperty("file.separator"), ""); //remove directory separators to prevent hacks
        
        //load config
        Configuration config = YabiConfiguration.getConfig();
        toolDirectory = config.getString("rsl.tools.directory");
        
        this.rslContent = "";
        
        //load RSL XML 
        loadRSL();
    }

    public String exportXML() {
        return this.rslContent.replaceAll("<argumentPlaceholder/>","");
    }

    //set the jobdir variable
    public void setJobDir(String directory) {
        this.rslContent = this.rslContent.replaceAll("#JOB_DIR#", directory);
    }
    
    public void setParamsFromBaat(BaatInstance bi) {
        ArrayList params = bi.getReconciledParameters();
        
        Iterator iter = params.iterator();
        while (iter.hasNext()) {
            String param = (String) iter.next();
            this.addParam(param);
        }
    }
    
    //prepend a <argument> node before the placeholder
    public void addParam(String param) {
        param = param.replaceAll("\\$","\\\\$");
        this.rslContent = this.rslContent.replaceAll("<argumentPlaceholder/>", "<argument>"+param+"</argument><argumentPlaceholder/>");
    }
    
    private void loadRSL() throws Exception {
        if (toolName != null) {
            String toolFileName = toolDirectory + toolName + ".rsl";
            FileReader fr     = new FileReader(toolFileName);
            BufferedReader br = new BufferedReader(fr);
            
            String line = "";
            while ((line = br.readLine()) != null) {
                this.rslContent += line;
            }
        }
    }

}
