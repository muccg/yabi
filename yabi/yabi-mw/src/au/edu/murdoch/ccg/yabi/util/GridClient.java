//
//  GridClient.java
//  yabi-mw
//
//  Created by ntt on 1/11/07.
//  Copyright 2007 CCG, Murdoch University. All rights reserved.
//
package au.edu.murdoch.ccg.yabi.util;

import java.util.*;
import java.net.*;
import java.io.*;
import javax.activation.DataHandler;
import au.edu.murdoch.ccg.yabi.objects.BaatInstance;
import au.edu.murdoch.ccg.yabi.objects.User;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.util.cog.YabiGridProxyInit;
import org.apache.commons.configuration.*;

import java.util.logging.Logger;

public class GridClient extends GenericProcessingClient {

    //instance variables
    private ArrayList inFiles;
    private ArrayList outFiles;
    private BaatInstance bi;
    private String jobStatus;
    private String jobId;
    private String inputDir;
    private String outputDir;
    private String rootDir;
    private String outFilePrefix = "";
    private String username = "";
    private String proxyCertLocation = "";
    private String gridType = "local"; // use this to specify which grid client is being executed. should be overridden by subclasses

    private static Logger logger = Logger.getLogger( AppDetails.getAppString() + "." + GridClient.class.getName());

    //constructors
    public GridClient( BaatInstance bi ) throws ConfigurationException {
        inFiles = new ArrayList();
        outFiles = new ArrayList();
        //we need to store the BaatInstance in this object so that we can modify it based on stagein of data
        this.bi = bi;

        loadConfig();
    }

    public GridClient() throws ConfigurationException {
        inFiles = new ArrayList();
        outFiles = new ArrayList();

        loadConfig();
    }

    private void loadConfig() throws ConfigurationException {
        //load config details
        Configuration conf = YabiConfiguration.getConfig();
        inputDir = conf.getString("yabi.rootDirectory");
        outputDir = inputDir;
        rootDir = conf.getString("yabi.rootDirectory");
    }

    //setter
    public void setOutputDir(String location) {
        this.outputDir = location;
    }

    public void setInputDirByUsername(String userName) {
        this.inputDir = rootDir + userName + "/";
        this.username = userName;
    }

    //instance methods
    public long submitJob () throws Exception {
        //create data directories
        String dataDirLoc = rootDir + this.outputDir ;
        File dataDir = new File(dataDirLoc);
        logger.fine("dataDir is: "+dataDirLoc);
        if (!dataDir.exists()) {
            dataDir.mkdir();
            logger.fine("had to create data dir");
        }

        //convert Baat into its XML
        String xmlString = bi.exportXML();

        //add attachment zip file
        if (bi.getAttachedFile() != null) {
            try {
                URL url = new URL(bi.getAttachedFile());
                /* DataHandler dataHandler = new DataHandler(url);
                AttachmentPart attachment = message.createAttachmentPart(dataHandler);
                attachment.setContentId("attached_file");

                call.addAttachmentPart(attachment);
                 */            
            } catch (Exception e) {
                //ignore faulty files
            }
        }

        //submit job
        
        return 0L;
    }

    public String getJobStatus (String jobId) throws Exception {
        this.jobId = jobId;  //store this for if we intend to stageout

        //debug only
        this.jobStatus = "C";
        return "C";
    }

    public void fileStageIn ( ArrayList files ) throws Exception {
        //file stagein for grendel is zip and submit as an attachment to the job
        inFiles = files;

        if (files != null && files.size() > 0) {
            //zip up all the input files and add the zipfile to the Baat
            String zipFileName = new Date().getTime() + ".zip";
            Zipper.createZipFile( zipFileName , inputDir, this.username, inFiles );

            bi.setAttachedFile("file://" + inputDir + zipFileName);
        }
    }

    //define a prefix to prepend to all staged out filenames to allow different tasks to not conflict
    public void setStageOutPrefix ( String prefix ) {
        this.outFilePrefix = prefix;
    }

    public void fileStageOut ( ArrayList files ) throws Exception {
        //file stageout for grendel is downloading and unzipping the results file
        /* URL zipFile = new URL(generateResultLocation(this.jobId));
                Zipper.unzip(zipFile, rootDir + outputDir, this.outFilePrefix);
         */
    }

    public boolean authenticate ( User user ) throws Exception {
        //check for a valid proxy for this user
        this.proxyCertLocation = this.rootDir + "/" + user.getUsername() + "/certificates/" + this.gridType + "_proxy.pem";
        
        YabiGridProxyInit ygpi = new YabiGridProxyInit();
                
        ygpi.verifyProxy(this.proxyCertLocation);
        
        return true; //only reaches here if proxy verified. if failed, exception is thrown
    }

    public boolean isCompleted () throws Exception {
        return (this.jobStatus.compareTo("C") == 0);
    }

    public boolean hasError () throws Exception {
        return (this.jobStatus.compareTo("E") == 0);
    }   


}