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
    private String jobStatus;
    private String jobId;

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
    public void setInputDirByUsername(String userName) {
        this.inputDir = rootDir + userName + "/";
    }

    //instance methods
    public String submitJob () throws Exception {
        //fake
        String jobId = "0";

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

                String stdOutPath = unitDirLoc + "/standardOutput.log";
                String stdErrPath = unitDirLoc + "/standardError.log";

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
        //file stagein for local is copying the input files to this node's directory so we can assume a flat infile dir
        inFiles = files;

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

        //iterate over files, copying them to our unitdir
        if (files != null && files.size() > 0) {
            Iterator iter = files.iterator();
            while (iter.hasNext()) {
                String fileIn = (String) iter.next();
                String subFileIn = fileIn;
                if (subFileIn.lastIndexOf("/") > 0) { //prune off path
                    subFileIn = subFileIn.substring(subFileIn.lastIndexOf("/")+1);
                }
                //put a file
                logger.fine("stagein: putting file: "+fileIn);

                File oldLoc = new File(this.inputDir + fileIn);
                File destLoc = new File(unitDir, subFileIn);

                copyFile(oldLoc, destLoc);
            }

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


    //------ HELPER FUNCTIONS ------ potentially spawn to helper class
    // Copies src file to dst file.
    // If the dst file does not exist, it is created
    public static void copyFile(File src, File dst) throws IOException {
        InputStream in = new FileInputStream(src);
        OutputStream out = new FileOutputStream(dst);
    
        // Transfer bytes from in to out
        byte[] buf = new byte[1024];
        int len;
        while ((len = in.read(buf)) > 0) {
            out.write(buf, 0, len);
        }
        in.close();
        out.close();
    }

}
