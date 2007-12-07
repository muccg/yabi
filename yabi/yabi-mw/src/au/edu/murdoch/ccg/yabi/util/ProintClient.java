package au.edu.murdoch.ccg.yabi.util;

import java.util.*;
import java.io.*;
import au.edu.murdoch.ccg.yabi.objects.BaatInstance;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import org.apache.commons.configuration.*;

import java.util.logging.Logger;

public class ProintClient extends GrendelClient {
    
    private static Logger logger = Logger.getLogger( AppDetails.getAppString() + "." + ProintClient.class.getName());
    
    //constructors
    public ProintClient( BaatInstance bi ) throws ConfigurationException {
        inFiles = new ArrayList();
        outFiles = new ArrayList();
        //we need to store the BaatInstance in this object so that we can modify it based on stagein of data
        this.bi = bi;
        
        loadConfig();
    }
    
    public ProintClient() throws ConfigurationException {
        inFiles = new ArrayList();
        outFiles = new ArrayList();
        
        loadConfig();
    }
    
    private void loadConfig() throws ConfigurationException {
    //load config details
    Configuration conf = YabiConfiguration.getConfig();
    grendelUrl = conf.getString("proint.url");
    inputDir = conf.getString("yabi.rootDirectory");
    outputDir = inputDir;
    rootDir = conf.getString("yabi.rootDirectory");
    grendelHost = conf.getString("proint.resultsLocation");
    }
    
}