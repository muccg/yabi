package au.edu.murdoch.ccg.yabi.util;

import java.util.*;
import java.net.*;
import java.io.*;
import au.edu.murdoch.ccg.yabi.objects.BaatInstance;
import au.edu.murdoch.ccg.yabi.objects.User;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import org.apache.commons.configuration.*;
import au.edu.murdoch.cbbc.util.*;

import java.util.logging.Logger;

public class LocalClient extends GenericProcessingClient {

    public static String inputDir;

    //instance variables
    private ArrayList inFiles;
    private ArrayList outFiles;
    private BaatInstance bi;
    private String jobStatus;
    private String jobId;
    private String outputDir;
    private String rootDir;
    private String outFilePrefix = "";

    private Logger logger = Logger.getLogger( AppDetails.getAppString() + "." + LocalClient.class.getName());

    //constructors
    public LocalClient( BaatInstance bi ) throws ConfigurationException {
        inFiles = new ArrayList();
        outFiles = new ArrayList();
        //we need to store the BaatInstance in this object so that we can modify it based on stagein of data
        this.bi = bi;

        loadConfig();
    }

    public LocalClient() throws ConfigurationException {
        inFiles = new ArrayList();
        outFiles = new ArrayList();

        loadConfig();
    }

    private void loadConfig() throws ConfigurationException {
        //load config details
        Configuration conf = YabiConfiguration.getConfig();
        //grendelUrl = conf.getString("grendel.url");
        rootDir = conf.getString("yabi.rootDirectory");
    }

    //setter
    public void setOutputDir(String location) {
        this.outputDir = location;
    }

    public void setInputDirByUsername(String userName) {
        this.inputDir = rootDir + userName + "/";
    }

    //instance methods
    public long submitJob () throws Exception {
        //fake
        long jobId = 0L;

        //test only
        try {
            //create data directories
            String dataDirLoc = rootDir + this.outputDir ;
            File dataDir = new File(dataDirLoc);
            if (!dataDir.exists()) {
                dataDir.mkdir();
            }
            String unitDirLoc = dataDirLoc + this.outFilePrefix;
            File unitDir = new File(unitDirLoc);
            if (!unitDir.exists()) {
                unitDir.mkdir();
            }

            String command = this.bi.getCommandLine();
            if ( command.indexOf(";") == -1 ) {
                logger.info("[command] "+this.bi.getCommandLine());
                Process proc = Runtime.getRuntime().exec(this.bi.getCommandLine(), null, unitDir);

                StreamWriter stdOutWriter = new StreamWriter();
                StreamWriter stdErrWriter = new StreamWriter();

                String stdOutPath = unitDirLoc + "/standardOutput.txt";
                String stdErrPath = unitDirLoc + "/standardError.txt";

                logger.fine("[out] "+stdOutPath);
                logger.fine("[err] "+stdErrPath);

                stdOutWriter.record(proc.getInputStream(), stdOutPath);
                stdErrWriter.record(proc.getErrorStream(), stdErrPath);

                //this is unnecessary, but let's stick around anyway
                int retval = proc.waitFor();
                if (retval != 0) {
                    throw new Exception("Command returned with a failure status");
                }
            }
        } catch (Exception e) {
            logger.severe("[command FAIL] "+e.getClass().getName()+" : "+e.getMessage());
            throw e;
        } catch (CBBCException e) {
            logger.severe("[command FAIL] "+e.getClass().getName()+" : "+e.getMessage());
            throw new Exception(e.getMessage(), e);
        }

        return jobId;
    }

    public String getJobStatus (String jobId) throws Exception {
        this.jobId = jobId;  //store this for if we intend to stageout

        //fake
        this.jobStatus = "C";

        return this.jobStatus;
    }

    public void fileStageIn ( ArrayList files ) throws Exception {
        //file stagein for local is nothing
        inFiles = files;

        if (files != null && files.size() > 0) {
        }
    }

    //define a prefix to prepend to all staged out filenames to allow different tasks to not conflict
    public void setStageOutPrefix ( String prefix ) {
        this.outFilePrefix = prefix;
    }

    public void fileStageOut ( ArrayList files ) throws Exception {
        //do nothing
    }

    public boolean authenticate ( User user ) throws Exception {
        //no authentication yet
        return true;
    }

    public boolean isCompleted () throws Exception {
        return true;
    }

    public boolean hasError () throws Exception {
        return false;
    }   

}
