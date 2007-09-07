package au.edu.murdoch.ccg.yabi.util;

import org.apache.axis.soap.*;
import javax.xml.soap.*;
import java.util.*;
import java.net.*;
import java.io.*;
import javax.activation.DataHandler;
import au.edu.murdoch.ccg.yabi.objects.BaatInstance;
import au.edu.murdoch.ccg.yabi.objects.User;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import org.apache.commons.configuration.*;

public class GrendelClient extends GenericProcessingClient {

    public static String grendelUrl;
    public static String inputDir;
    public static String grendelHost;

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
    public GrendelClient( BaatInstance bi ) throws ConfigurationException {
        inFiles = new ArrayList();
        outFiles = new ArrayList();
        //we need to store the BaatInstance in this object so that we can modify it based on stagein of data
        this.bi = bi;

        loadConfig();
    }

    public GrendelClient() throws ConfigurationException {
        inFiles = new ArrayList();
        outFiles = new ArrayList();

        loadConfig();
    }

    private void loadConfig() throws ConfigurationException {
        //load config details
        Configuration conf = YabiConfiguration.getConfig();
        grendelUrl = conf.getString("grendel.url");
        inputDir = conf.getString("yabi.rootDirectory");
        outputDir = inputDir;
        rootDir = conf.getString("yabi.rootDirectory");
        grendelHost = conf.getString("grendel.resultsLocation");
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
        //create data directories
        String dataDirLoc = rootDir + this.outputDir ;
        File dataDir = new File(dataDirLoc);
        System.out.println("dataDir is: "+dataDirLoc);
        if (!dataDir.exists()) {
            dataDir.mkdir();
            System.out.println("had to create data dir");
        }

        //convert Baat into its XML
        String xmlString = bi.exportXML();

        //DEBUG
        //System.out.println("\n\n" + xmlString + "\n\n");

        //create SOAP message
        MessageFactory factory = MessageFactory.newInstance();
        SOAPMessage message = factory.createMessage();

        //defined our body as a submitXMLJob call
        SOAPBody body = message.getSOAPBody();
        SOAPFactory soapFactory = SOAPFactory.newInstance();
        Name bodyName = soapFactory.createName("submitXMLJob", "", "urn:Grendel");
        SOAPBodyElement bodyElement = body.addBodyElement(bodyName); 
    
        //add our xmlString as an argument
        Name name = soapFactory.createName("task");
        SOAPElement xmlStringElem = bodyElement.addChildElement(name);
        xmlStringElem.addTextNode(xmlString); 

        //prepare to make connection to grendel
        SOAPConnectionFactory soapConnectionFactory = SOAPConnectionFactory.newInstance();
        SOAPConnection connection = soapConnectionFactory.createConnection();
      
        java.net.URL endpoint = new URL(grendelUrl);

        //add attachment zip file
        if (bi.getAttachedFile() != null) {
            try {
                URL url = new URL(bi.getAttachedFile());
                DataHandler dataHandler = new DataHandler(url);
                AttachmentPart attachment = message.createAttachmentPart(dataHandler);
                attachment.setContentId("attached_file");

                message.addAttachmentPart(attachment);
            } catch (Exception e) {
                //ignore faulty files
            }
        }

        //make the SOAP call
        SOAPMessage response = connection.call(message, endpoint);

        //examine response
        SOAPHeader header = response.getSOAPHeader();
        SOAPBody rbody = response.getSOAPBody();

        //check for a fault
        if ( rbody.hasFault() ) {

            SOAPFault newFault = rbody.getFault();
            Name code = newFault.getFaultCodeAsName();
            String string = newFault.getFaultString();

            connection.close();

            //clean up staged in file
            if (bi.getAttachedFile() != null) {
                try {
                    URI uri = new URI(bi.getAttachedFile());
                    File doomed = new File(uri);
                    doomed.delete();
                } catch (Exception e) {
                    //ignore faulty files
                }
            }

            throw new Exception("SOAP Fault: " + string);

        } else {

            //fetch grendel ID from response
            //this number is stored in the following hierarchy
            //<Body><submitXMLJobResponse><submitXMLJobReturn>0000001</></></>
            SOAPElement jobResponse = (SOAPElement) rbody.getChildElements().next();
            SOAPElement jobReturn = (SOAPElement) jobResponse.getChildElements().next();
            long jobId = 0L;

            try {
                jobId = Long.parseLong( jobReturn.getValue() );
            } catch (NumberFormatException e) {
                System.out.println("ERROR PARSING NUMBER ------");
                System.out.println("jobReturn : " + jobReturn + " :::: " + jobReturn.getValue());
            }

            //close SOAP connection
            connection.close();

            //clean up staged in file
            if (bi.getAttachedFile() != null) {
                try {
                    URI uri = new URI(bi.getAttachedFile());
                    File doomed = new File(uri);
                    doomed.delete();
                } catch (Exception e) {
                    //ignore faulty files
                }
            } 

           //return grendel ID
            return jobId;

        }

    }

    public String getJobStatus (String jobId) throws Exception {
        this.jobId = jobId;  //store this for if we intend to stageout

        MessageFactory factory = MessageFactory.newInstance();
        SOAPMessage message = factory.createMessage();

        SOAPBody body = message.getSOAPBody();
        SOAPFactory soapFactory = SOAPFactory.newInstance();
        Name bodyName = soapFactory.createName("getJobStatus", "", "urn:Grendel");
        SOAPBodyElement bodyElement = body.addBodyElement(bodyName); 
    
        Name name = soapFactory.createName("id");
        SOAPElement xmlStringElem = bodyElement.addChildElement(name);
        xmlStringElem.addTextNode(jobId);

        SOAPConnectionFactory soapConnectionFactory = SOAPConnectionFactory.newInstance();
        SOAPConnection connection = soapConnectionFactory.createConnection();
        
        java.net.URL endpoint = new URL(grendelUrl);

        SOAPMessage response = connection.call(message, endpoint);

        SOAPHeader header = response.getSOAPHeader();
        SOAPBody rbody = response.getSOAPBody();

        //check for a fault
        if ( rbody.hasFault() ) {

            SOAPFault newFault = rbody.getFault();
            Name code = newFault.getFaultCodeAsName();
            String string = newFault.getFaultString();

            connection.close();

            throw new Exception(string);

        } else {

            java.util.Iterator iterator = rbody.getChildElements();
            SOAPElement element = (SOAPElement)iterator.next(); //getJobStatusResponse
            iterator = element.getChildElements();
            SOAPElement wantedElement = (SOAPElement)iterator.next(); //getJobStatusReturn

            connection.close();

            this.jobStatus = wantedElement.getValue();

            return this.jobStatus;

        }
    }

    public void fileStageIn ( ArrayList files ) throws Exception {
        //file stagein for grendel is zip and submit as an attachment to the job
        inFiles = files;

        if (files != null && files.size() > 0) {
            //zip up all the input files and add the zipfile to the Baat
            String zipFileName = new Date().getTime() + ".zip";
            Zipper.createZipFile( zipFileName , inputDir, inFiles );

            bi.setAttachedFile("file://" + inputDir + zipFileName);
        }
    }

    //define a prefix to prepend to all staged out filenames to allow different tasks to not conflict
    public void setStageOutPrefix ( String prefix ) {
        this.outFilePrefix = prefix;
    }

    public void fileStageOut ( ArrayList files ) throws Exception {
        //file stageout for grendel is downloading and unzipping the results file
        URL zipFile = new URL(generateResultLocation(this.jobId));
        Zipper.unzip(zipFile, rootDir + outputDir, this.outFilePrefix);
    }

    public boolean authenticate ( User user ) throws Exception {
        //grendel has no authentication yet
        return true;
    }

    public boolean isCompleted () throws Exception {
        return (this.jobStatus.compareTo("C") == 0);
    }

    public boolean hasError () throws Exception {
        return (this.jobStatus.compareTo("E") == 0);
    }   

    //this is particular to grendel
    private String generateResultLocation(String jobId) {
        String dirName = jobId.substring(0,9);
        String result = grendelHost + "/" + dirName + "/" + jobId + ".zip";

        return result;
    }

}
