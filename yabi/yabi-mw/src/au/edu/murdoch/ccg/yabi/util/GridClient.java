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
import au.edu.murdoch.ccg.yabi.objects.RSLInstance;
import au.edu.murdoch.ccg.yabi.objects.User;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.util.cog.YabiGridProxyInit;
import org.apache.commons.configuration.*;

import java.security.cert.*;
import org.globus.ftp.*;
import org.globus.gsi.*;
import org.ietf.jgss.GSSCredential;
import org.globus.gsi.gssapi.GlobusGSSCredentialImpl;
import org.globus.exec.client.GramJob;
import org.globus.ftp.exception.ServerException;
import org.globus.common.ResourceManagerContact;
import org.globus.wsrf.client.*;
import org.apache.axis.message.addressing.EndpointReferenceType;
import org.apache.axis.message.addressing.EndpointReference;
import org.globus.exec.generated.ManagedJobFactoryPortType;
import org.globus.wsrf.impl.security.authorization.HostAuthorization;
import org.globus.wsrf.impl.security.descriptor.ClientSecurityDescriptor;
import org.globus.wsrf.security.Constants;
import javax.xml.rpc.Stub;
import org.globus.exec.generated.CreateManagedJobInputType;
import org.globus.exec.generated.CreateManagedJobOutputType;
import org.apache.axis.message.addressing.AttributedURI;
import org.apache.axis.components.uuid.UUIDGenFactory;
import org.oasis.wsrf.properties.GetResourcePropertyResponse;
import org.globus.exec.utils.ManagedJobConstants;
import org.globus.transfer.reliable.service.factory.DelegationServiceEndpoint;
import org.globus.delegation.DelegationUtil;
import org.apache.axis.message.addressing.ReferenceParametersType;

import org.globus.exec.utils.rsl.RSLHelper;
import org.globus.exec.utils.client.ManagedJobFactoryClientHelper;
import org.globus.exec.utils.ManagedJobFactoryConstants;
import org.globus.exec.utils.client.ManagedJobClientHelper;
import org.globus.exec.generated.JobDescriptionType;
import org.gridforum.jgss.ExtendedGSSManager;
import org.globus.exec.generated.StateEnumeration;
import org.apache.axis.message.MessageElement;
import org.globus.wsrf.encoding.ObjectDeserializer;
import org.globus.wsrf.encoding.ObjectSerializer;
import org.w3c.dom.*;
import javax.xml.parsers.*;

import javax.xml.namespace.QName;

import org.globus.axis.util.Util;

import java.util.logging.Logger;

public class GridClient extends GenericProcessingClient {

    static {
        Util.registerTransport();
    }
    
    
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
    private String gridType = "ivec"; // use this to specify which grid client is being executed.
    private String gridFTPHost = "";
    private int gridFTPPort = 0;
    private String gridWSURL = "";
    private String gridWSJobURL = "";
    private String gridFTPDefaultBaseDir = "";
    private String gridFTPBaseDir = "";
    Configuration conf = null;
    private String gridMD5 = ""; //use this for creating a stagein/out directory for this job on the grid

    private static Logger logger = Logger.getLogger( AppDetails.getAppString() + "." + GridClient.class.getName());

    //constructors
    public GridClient( BaatInstance bi ) throws ConfigurationException {
        inFiles = new ArrayList();
        outFiles = new ArrayList();
        //we need to store the BaatInstance in this object so that we can modify it based on stagein of data
        this.bi = bi;
        //we should use the baat to tell us where this grid tool is being run. eg ivec, ccg, etc
        
        
        loadConfig();
    }

    public GridClient() throws ConfigurationException {
        inFiles = new ArrayList();
        outFiles = new ArrayList();

        loadConfig();
    }

    private void loadConfig() throws ConfigurationException {
        //load config details
        this.conf = YabiConfiguration.getConfig();
        inputDir = conf.getString("yabi.rootDirectory");
        outputDir = inputDir;
        rootDir = conf.getString("yabi.rootDirectory");
        
        //short-term, load ivec details
        this.gridFTPHost = this.conf.getString("gridftp.host.ivec.hostname");
        this.gridFTPPort = this.conf.getInt("gridftp.host.ivec.port");
        this.gridFTPDefaultBaseDir = this.conf.getString("gridftp.host.ivec.defaultBaseDir");
        this.gridFTPBaseDir = this.gridFTPDefaultBaseDir;
        this.gridWSURL = this.conf.getString("grid.host.ivec.wsurl");
        this.gridWSJobURL = this.conf.getString("grid.host.ivec.wsjoburl");
    }

    //setter
    public void setOutputDir(String location) {
        this.outputDir = location;
        
        //use the outputDir as a unique identifier for this job, used to create a unique stagein/out dir on the grid
        try {
            MD5 hasher = MD5.getInstance();
            this.gridMD5 = hasher.hashData(location.getBytes());
        } catch (Exception e) {
            logger.info("MD5 failure: "+e.getMessage());
        }
    }

    public void setInputDirByUsername(String userName) {
        this.inputDir = rootDir + userName + "/";
        this.username = userName;
    }

    //instance methods
    public String submitJob () throws Exception {
        //create data directories
        String dataDirLoc = rootDir + this.outputDir ;
        File dataDir = new File(dataDirLoc);
        logger.fine("dataDir is: "+dataDirLoc);
        if (!dataDir.exists()) {
            dataDir.mkdir();
            logger.fine("had to create data dir");
        }

        //create data directories
        String unitDirLoc = dataDirLoc + this.outFilePrefix;
        File unitDir = new File(unitDirLoc);
        if (!unitDir.exists()) {
            unitDir.mkdir();
        }
        
        //convert Baat into its XML
        String xmlString = bi.exportXML();

        //submit job

        //load job rsl
        RSLInstance rsl = new RSLInstance(bi.getToolName());
        rsl.setJobDir(this.gridMD5);
        rsl.setParamsFromBaat(bi);
        logger.info("RSL: "+rsl.exportXML());
        
        JobDescriptionType jobDescription = RSLHelper.readRSL(rsl.exportXML());
        
        //set connection options
        URL factoryUrl = ManagedJobFactoryClientHelper.getServiceURL(this.gridWSURL + "/wsrf/services/ManagedJobFactoryService").getURL();
        String factoryType = ManagedJobFactoryConstants.FACTORY_TYPE.PBS;
        EndpointReferenceType factoryEndpoint = ManagedJobFactoryClientHelper.getFactoryEndpoint(factoryUrl, factoryType);
        ManagedJobFactoryPortType factoryPort = ManagedJobFactoryClientHelper.getPort(factoryEndpoint);
        
        logger.fine("factoryURL: "+factoryUrl+"    factoryType: "+factoryType);
        
        //credentials
        GSSCredential credential;
        GlobusCredential globusCredential;
        
        globusCredential = new GlobusCredential( this.proxyCertLocation );
        credential = new GlobusGSSCredentialImpl( globusCredential, GSSCredential.INITIATE_AND_ACCEPT );    
        //set default credential to prevent accidental loading of default globus proxy files
        GlobusCredential.setDefaultCredential(globusCredential);
        
        //(nick: wringing through the extendedgssmanager is a vague attempt to voodoo magic it to work)
        // security setup - sorry can't really explain this but it is
        //             crucial to get job submission working correctly
        ExtendedGSSManager manager = (ExtendedGSSManager)ExtendedGSSManager.getInstance();
        credential = manager.createCredential(GSSCredential.INITIATE_AND_ACCEPT);
        globusCredential = ((GlobusGSSCredentialImpl)credential).getGlobusCredential();
        
        //set security
        HostAuthorization iA = new HostAuthorization();
        ClientSecurityDescriptor secDesc = new ClientSecurityDescriptor();
        secDesc.setGSITransport(GSIConstants.ENCRYPTION);
        secDesc.setAuthz(iA);
        secDesc.setGSSCredential(credential);
        secDesc.setProxyFilename(this.proxyCertLocation);
        ((Stub) factoryPort)._setProperty(Constants.CLIENT_DESCRIPTOR, secDesc);
        
        Calendar cal = Calendar.getInstance();
        cal.add(java.util.Calendar.HOUR,50);
        
        //generate unique ID for referencing job later
        String uuid = UUIDGenFactory.getUUIDGen().nextUUID();
        
        CreateManagedJobInputType jobInput = new CreateManagedJobInputType();
        jobInput.setJobID(new AttributedURI("uuid:" + uuid));
        jobInput.setInitialTerminationTime(cal);
        jobInput.setJob(jobDescription);
        
        CreateManagedJobOutputType createResponse = factoryPort.createManagedJob(jobInput);
        EndpointReferenceType jobEndpoint = createResponse.getManagedJobEndpoint();

        logger.info("submitted, jobEndpoint : "+jobEndpoint);
        
        logger.finest("EPRXML: "+ObjectSerializer.toString(jobEndpoint, new QName("http://schemas.xmlsoap.org/ws/2004/03/addressing", "EndpointReferenceType")));
        
        return ObjectSerializer.toString(jobEndpoint, new QName("http://schemas.xmlsoap.org/ws/2004/03/addressing", "EndpointReferenceType"));
    }

    public String getJobStatus (String jobId) throws Exception {
        this.jobId = jobId;  //store this for if we intend to stageout

        logger.fine("getting status for grid epr: "+jobId);
        
        byte[] bytes = jobId.getBytes();
        ByteArrayInputStream bais = new ByteArrayInputStream(bytes);
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        DocumentBuilder db = dbf.newDocumentBuilder();
        Document eprDoc = db.parse(bais);
        
        EndpointReferenceType factoryEndpoint = (EndpointReferenceType) ObjectDeserializer.toObject(eprDoc.getDocumentElement(), EndpointReferenceType.class);
        logger.info("epr: "+factoryEndpoint);
        ManagedJobFactoryPortType factoryPort = ManagedJobFactoryClientHelper.getPort(factoryEndpoint);
        
        //credentials
        GSSCredential credential;
        GlobusCredential globusCredential;
        
        globusCredential = new GlobusCredential( this.proxyCertLocation );
        logger.fine("using grid proxy file: "+this.proxyCertLocation);
        
        credential = new GlobusGSSCredentialImpl( globusCredential, GSSCredential.INITIATE_AND_ACCEPT );    
        //set default credential to prevent accidental loading of default globus proxy files
        GlobusCredential.setDefaultCredential(globusCredential);
        
        //(nick: wringing through the extendedgssmanager is a vague attempt to voodoo magic it to work)
        // security setup - sorry can't really explain this but it is
        //             crucial to get job submission working correctly
        ExtendedGSSManager manager = (ExtendedGSSManager)ExtendedGSSManager.getInstance();
        credential = manager.createCredential(GSSCredential.INITIATE_AND_ACCEPT);
        globusCredential = ((GlobusGSSCredentialImpl)credential).getGlobusCredential();
        
        //set security
        HostAuthorization iA = new HostAuthorization();
        ClientSecurityDescriptor secDesc = new ClientSecurityDescriptor();
        secDesc.setGSITransport(GSIConstants.ENCRYPTION);
        secDesc.setAuthz(iA);
        secDesc.setGSSCredential(credential);
        secDesc.setProxyFilename(this.proxyCertLocation);
        ((Stub) factoryPort)._setProperty(Constants.CLIENT_DESCRIPTOR, secDesc);
        
        GetResourcePropertyResponse response = factoryPort.getResourceProperty(ManagedJobConstants.RP_STATE);
        MessageElement [] any = response.get_any();
        StateEnumeration state = (StateEnumeration) ObjectDeserializer.toObject(any[0], StateEnumeration.class);
        
        logger.info("Grid job state: "+state);
        
        //translate to generic values
        this.jobStatus = "R";
        if (state.equals(StateEnumeration.Unsubmitted) || state.equals(StateEnumeration.Pending)) {
            this.jobStatus = "Q";
        } else if (state.equals(StateEnumeration.Failed)) {
            this.jobStatus = "E";
        } else if (state.equals(StateEnumeration.Done)) {
            this.jobStatus = "C";
        }
        
        return this.jobStatus;
    }

    public void fileStageIn ( ArrayList files ) throws Exception {
        //connect, fetch a list of files and download them all
        GridFTPClient client = new GridFTPClient(this.gridFTPHost, this.gridFTPPort);
        
        try {
            //file stagein for grid is gridftp put
            inFiles = files;

            if (files != null && files.size() > 0) {
                
                GSSCredential credential;
                GlobusCredential globusCredential;
                
                globusCredential = new GlobusCredential( this.proxyCertLocation );
                credential = new GlobusGSSCredentialImpl( globusCredential, GSSCredential.INITIATE_AND_ACCEPT );    
                
                ((GridFTPClient)client).authenticate(credential);

                //arbitrary default
                client.setProtectionBufferSize(1048576);
                
                logger.info("stagein: gridFTP connect");
                
                client.setDataChannelProtection(GridFTPSession.PROTECTION_PRIVATE);
                logger.info("stagein: data channel protection = " + client.getDataChannelProtection());
                
                //create a directory for this job
                String jobDir = this.gridFTPBaseDir + this.gridMD5;
                logger.info("stagein: making dir: "+jobDir);

                client.makeDir(jobDir);
                jobDir = jobDir + "/";
                
                Iterator iter = files.iterator();
                while (iter.hasNext()) {
                    String fileIn = (String) iter.next();
                    String subFileIn = fileIn;
                    if (subFileIn.lastIndexOf("/") > 0) { //prune off path
                        subFileIn = subFileIn.substring(subFileIn.lastIndexOf("/")+1);
                    }
                    //put a file
                    logger.fine("stagein: putting file: "+fileIn);
                    client.setPassiveMode(true);
                    client.put(new File(inputDir + fileIn), jobDir + subFileIn, false);
                    logger.info("stagein: sent: "+fileIn);
                }
                
            }
        } catch (Exception e) {
            throw e;
        } finally {
            try {
                client.close();
            } catch (Exception ce) {}
            logger.info("stagein: closing ftp connection");
        }
    }

    //define a prefix to prepend to all staged out filenames to allow different tasks to not conflict
    public void setStageOutPrefix ( String prefix ) {
        this.outFilePrefix = prefix;
    }

    public void fileStageOut ( ArrayList files ) throws Exception {
        //connect, fetch a list of files and download them all
        GridFTPClient client = new GridFTPClient(this.gridFTPHost, this.gridFTPPort);
        
        try {
            
            GSSCredential credential;
            GlobusCredential globusCredential;
            
            globusCredential = new GlobusCredential( this.proxyCertLocation );
            credential = new GlobusGSSCredentialImpl( globusCredential, GSSCredential.INITIATE_AND_ACCEPT );    
            
            ((GridFTPClient)client).authenticate(credential);
            
            client.setProtectionBufferSize(1048576);
            
            logger.info("stageout: gridFTP connect");
            
            client.setDataChannelProtection(GridFTPSession.PROTECTION_PRIVATE);

            String remoteDir = this.gridFTPBaseDir + this.gridMD5 + "/";
            
            String stageOutDir = this.rootDir + this.outputDir + this.outFilePrefix + "/";

            client.setPassiveMode(true);
            Vector outFiles = client.list(remoteDir);
            
            logger.info("stageout: gridFTP listing shows: " + outFiles);
            
            Iterator iter = outFiles.iterator();
            while (iter.hasNext()) {
                FileInfo fi = (FileInfo) iter.next();
                String fileOut = fi.getName();
                if (!fi.isDirectory()) {
                    //get a file
                    logger.info("stageout: trying to GET : "+remoteDir + fileOut+ " output to: "+ stageOutDir + fileOut);
                    try {
                        client.setPassiveMode(true);
                        client.get(remoteDir + fileOut, new File(stageOutDir + fileOut)); 
                        client.deleteFile(remoteDir + fileOut);
                        logger.info("stageout: fetched and deleted: "+remoteDir + fileOut);
                    } catch (ServerException se) {
                        logger.warning("stageout: ignoring server exception: "+se.getMessage());
                    }
                    logger.info("stageout: received "+fileOut);
                } else {
                    logger.fine("skipping download of directory "+fileOut);
                }
            }
            
            //delete directory
            logger.info("stageout: deleting grid dir: "+remoteDir);
            client.deleteDir(remoteDir);
        } catch (Exception e) {
            throw e;
        } finally {
            try {
                client.close();
            } catch (Exception ce) {}
            logger.info("stage out: closing ftp connection");
        }
    }

    public boolean authenticate ( User user ) throws Exception {
        //init certs
        this.initializeTrustedCerts();
        
        //check for a valid proxy for this user
        this.proxyCertLocation = this.rootDir + "/" + user.getUsername() + "/certificates/" + this.gridType + "_proxy.pem";
        
        //load user-specific grid parameters
        //throw a friendly error if config fails
        try {
            Configuration userGridConf = new PropertiesConfiguration(this.rootDir + "/" + user.getUsername() + "/certificates/" + this.gridType + ".cfg");
            this.gridFTPBaseDir = userGridConf.getString("scratchdir");
        } catch (ConfigurationException ce) {
            throw new Exception("Error loading user grid configuration");
        }
        
        YabiGridProxyInit ygpi = new YabiGridProxyInit();
                
        ygpi.verifyProxy(this.proxyCertLocation);
                
        logger.info("proxy file verified");
        
        return true; //only reaches here if proxy verified. if failed, exception is thrown
    }
    
    public void initializeTrustedCerts() {
        try {
            //APAC GRID CERT
            InputStream ainStream = new FileInputStream("/yabi/certificates/apac.crt");
            InputStream binStream = new FileInputStream("/yabi/certificates/apac0.crt");
            CertificateFactory cf = CertificateFactory.getInstance("X.509");
            X509Certificate certs[] = {(X509Certificate)cf.generateCertificate(ainStream), (X509Certificate)cf.generateCertificate(binStream)};
            ainStream.close();
            binStream.close();
            
            TrustedCertificates.setDefaultTrustedCertificates(new TrustedCertificates(certs));
            
            //REVOCATION LISTS
            CertificateRevocationLists crl = CertificateRevocationLists.getCertificateRevocationLists("/yabi/certificates/1e12d831.r0,/yabi/certificates/21bf4d92.r0");
            CertificateRevocationLists.setDefaultCertificateRevocationList(crl);
            X509CRL[] revLists = crl.getCrls();
            logger.info("list of revocation lists");
            for (int i = 0; i < revLists.length; i++) {
                logger.info("revocation list " + i + "=" + revLists[i].getNextUpdate());
            }
            
        } catch (Exception e) {
            logger.severe("failed to load trusted certs");
        }
    }

    public boolean isCompleted () throws Exception {
        return (this.jobStatus.compareTo("C") == 0);
    }

    public boolean hasError () throws Exception {
        return (this.jobStatus.compareTo("E") == 0);
    }   


}
