//
//  CCGGridClient.java
//  yabi-mw
//
//  Created by ntt on 29/07/2008.
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
import org.globus.exec.utils.service.ManagedJobHelper;
import org.w3c.dom.*;
import javax.xml.parsers.*;
import au.edu.murdoch.cbbc.util.CBBCException;


import javax.xml.namespace.QName;

import org.globus.axis.util.Util;

import java.util.logging.Logger;

public class CCGGridClient extends GridClient {

    static {
        Util.registerTransport();
    }
    
    protected static Logger logger = Logger.getLogger( AppDetails.getAppString() + "." + CCGGridClient.class.getName());

    //constructors
    public CCGGridClient( BaatInstance bi ) throws ConfigurationException {
        inFiles = new ArrayList();
        outFiles = new ArrayList();
        //we need to store the BaatInstance in this object so that we can modify it based on stagein of data
        this.bi = bi;
        //we should use the baat to tell us where this grid tool is being run. eg ivec, ccg, etc
       
        loadConfig();
    }

    public CCGGridClient() throws ConfigurationException {
        inFiles = new ArrayList();
        outFiles = new ArrayList();

        loadConfig();
    }

    protected String getGridType() {
        return "ccg";
    }

    private void loadConfig() throws ConfigurationException {
        //load config details
        this.conf = YabiConfiguration.getConfig();
        inputDir = conf.getString("yabi.rootDirectory");
        outputDir = inputDir;
        rootDir = conf.getString("yabi.rootDirectory");
        
        //short-term, load ivec details
        this.gridFTPHost = this.conf.getString("gridftp.host.ccg.hostname");
        this.gridFTPPort = this.conf.getInt("gridftp.host.ccg.port");
        this.gridFTPDefaultBaseDir = this.conf.getString("gridftp.host.ccg.defaultBaseDir");
        this.gridFTPBaseDir = this.gridFTPDefaultBaseDir;
        this.gridWSURL = this.conf.getString("grid.host.ccg.wsurl");
        this.gridWSJobURL = this.conf.getString("grid.host.ccg.wsjoburl");
    }

}
