package au.edu.murdoch.ccg.yabi.util;

import java.util.*;
import java.net.*;
import java.io.*;
import au.edu.murdoch.ccg.yabi.objects.BaatInstance;
import au.edu.murdoch.ccg.yabi.objects.User;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import org.apache.commons.configuration.*;

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
    }

    //setter
    public void setOutputDir(String location) {
        this.outputDir = location;
    }

    public void setInputDirByUsername(String userName) {
        this.inputDir = rootDir + userName + "/data/";
    }

    //instance methods
    public long submitJob () throws Exception {
        //fake
        long jobId = 0L;

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
