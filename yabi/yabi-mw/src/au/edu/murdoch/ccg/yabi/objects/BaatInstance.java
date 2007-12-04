package au.edu.murdoch.ccg.yabi.objects;

import org.dom4j.*; 
import java.util.*;
import java.io.*;
import org.dom4j.io.*;
import java.net.*;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.util.AppDetails;
import org.apache.commons.configuration.*;
import au.edu.murdoch.cbbc.util.CBBCException;
import org.xml.sax.EntityResolver;
import org.xml.sax.InputSource;

import java.util.logging.Logger;

public class BaatInstance {

    private String toolDefinitionDirectory;

    private String toolName;
    private ArrayList parameters;
    private ArrayList inputFiles;
    private ArrayList outputFiles;
    private Document baatFile;
    private String attachedFile;
    private String toolPath;
    private String rootDir;
    private String username; //optional, used for prependUserDir option
    private boolean symlinkOutputDir;

    private static Logger logger = Logger.getLogger( AppDetails.getAppString() + "." + BaatInstance.class.getName());

    public BaatInstance(String toolName) throws Exception {
        //init vars
        this.toolName = toolName.replaceAll(System.getProperty("file.separator"), ""); //remove directory separators to prevent hacks

        //load config
        Configuration config = YabiConfiguration.getConfig();
        toolDefinitionDirectory = config.getString("baat.tools.definitionDirectory");
        rootDir = config.getString("yabi.rootDirectory");

        parameters = new ArrayList();
        inputFiles = new ArrayList();
        outputFiles = new ArrayList();

        username = "";

        //load Baat XML for use in validating and identifying input and output files
        loadBaat();
    }

    public ArrayList getParameters() {
        return this.parameters;
    }  
    
    /**
     * force parameters into a format usable by RSLInstance
     */
    public ArrayList getReconciledParameters() {
        this.reconcileParams();
        ArrayList simpleParams = new ArrayList();
        
        //append all parameters to the end
        //TODO do this in a particular order
        Iterator iter = this.parameters.iterator();
        while (iter.hasNext()) {
            BaatParameter bp = (BaatParameter) iter.next();
            
            String tempValue = bp.value;
            
            //remove path elements from filenames, as once it is staged in via GridFTP there is no path
            if (bp.inputFile.compareTo("yes") == 0) {
                if (tempValue.lastIndexOf(System.getProperty("file.separator")) > -1) {
                    tempValue = tempValue.substring(tempValue.lastIndexOf(System.getProperty("file.separator")) + 1);    
                }
            }
            
            if (bp.filter != null && bp.filter.equalsIgnoreCase("prependRootDir")) {
                tempValue = rootDir + bp.value;
            } else if (bp.filter != null && bp.filter.equalsIgnoreCase("prependUserDir")) {
                tempValue = rootDir + username + "/" + bp.value;
            } else if (bp.filter != null && bp.filter.equalsIgnoreCase("../../")) {
                tempValue = "../../" + bp.value;
            }
            
            if (bp.switchUse.equalsIgnoreCase("both")) {
                simpleParams.add( bp.switchName );
                simpleParams.add( tempValue );
            } else if (bp.switchUse.equalsIgnoreCase("valueOnly")) {
                simpleParams.add( tempValue );
            } else if (bp.switchUse.equalsIgnoreCase("switchOnly")) {
                simpleParams.add( bp.switchName );
            }
        }
        
        return simpleParams;
    }

    public ArrayList getOutputFiles() {
        return this.outputFiles;
    }

    public ArrayList getInputFiles() {
        return this.inputFiles;
    }

    public String getAttachedFile() {
        return this.attachedFile;
    }

    public String getToolName() {
        return this.toolName;
    }
    
    public void setAttachedFile(String fileLoc) {
        this.attachedFile = fileLoc;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public boolean getSymlinkOutputDir() {
        return this.symlinkOutputDir;
    }

    public String exportXML() {
        //process the contents of this Baat and convert to the simplest XML output that can be used by Grendel, for instance
        
        //call to strip out unused params
        reconcileParams();

        return baatFile.asXML();
    }

    private void reconcileParams() {
        setSourceParams(); //chance to propagate input parameters, ie input files being used to create outputfilenames
        
        Element paramList = (Element) baatFile.selectSingleNode("//parameterList");

        List results = paramList.elements();
        for ( Iterator iter = results.iterator(); iter.hasNext(); ) {
            Element element = (Element) iter.next();

            //compare against in-memory parameters            
            for ( Iterator parmIter = parameters.iterator(); parmIter.hasNext(); ) {
                BaatParameter bp = (BaatParameter) parmIter.next();
                if ( (bp.rank.length() > 0 && bp.rank.compareTo(element.attributeValue("rank")) == 0)   ||
                     bp.switchName.compareTo(element.attributeValue("switch")) == 0 ) {

                    //it is a match, so set values or remove depending on isSet status in-memory

                    if (bp.isSet) {
                        element.addAttribute("value", bp.value);
                    } else {
                        element.detach();
                        //remove from in-memory array if not set
                        parmIter.remove();
                    }
                }
            }
        }

        //strip out parameteraliaslist contents and any outputExtension elements
        XPath xpathSelector = DocumentHelper.createXPath("//outputExtension");
        results = xpathSelector.selectNodes(baatFile);
        for ( Iterator iter = results.iterator(); iter.hasNext(); ) {
            Element elem = (Element) iter.next();
            elem.detach();
        }

        xpathSelector = DocumentHelper.createXPath("//parameterAlias");
        results = xpathSelector.selectNodes(baatFile);
        for ( Iterator iter = results.iterator(); iter.hasNext(); ) {
            Element elem = (Element) iter.next();
            elem.detach();
        }

        if (attachedFile != null && attachedFile.length() > 0) {
            Element inputFileNode = (Element) baatFile.selectSingleNode("//inputFile");

            String attach = attachedFile;
            //remove all file path info, we just want the filename itself
            int lastLoc = attach.lastIndexOf( System.getProperty("file.separator") );
            if (lastLoc > -1) {
                attach = attach.substring(lastLoc + 1);
            }

            inputFileNode.setText( attach );        
        }

        //TODO use a real user name
        Element submitUserNode = (Element) baatFile.selectSingleNode("//submitUser");
        submitUserNode.setText( this.username );

        //set priority
        Element priorityNode = (Element)baatFile.selectSingleNode("//priority");
        priorityNode.setText("-10");

        //get grendel based xml elements
        Element grendelNode = (Element)baatFile.selectSingleNode("//grendel");
        Element optionEl = grendelNode.addElement("option");
        Element nameEl = optionEl.addElement("name");
        nameEl.setText("yabi");
    }

    public void setGrendelOption(String key, String value) {
        //get grendel based xml elements
        Element grendelNode = (Element)baatFile.selectSingleNode("//grendel");
        Element submitLabel = (Element)baatFile.selectSingleNode("//submitLabel");

        //check for specific options
        if (key.compareTo("eric") == 0 && value.length() > 0) {
            Element dummyOptionEl = grendelNode.addElement("option");
            Element dummyNameEl = dummyOptionEl.addElement("name");
            dummyNameEl.setText("dummy");

            Element optionEl = grendelNode.addElement("option");
            Element nameEl = optionEl.addElement("name");
            nameEl.setText("eric");

            submitLabel.setText(value);
        } else {
            logger.fine("[BaatInstance] failed to set grendelOption ["+key+"] = ["+value+"]");
        }
    }

    private void loadBaat() throws Exception {
        if (toolName != null) {
            String toolFileName = toolDefinitionDirectory + toolName + ".xml";
            URL toolFile = new URL(toolFileName);

            //implement manual entity resolver to prevent network requests for baat dtd
            EntityResolver resolver = new EntityResolver() {
                public InputSource resolveEntity(String publicId, String systemId) {
                    InputStream in = getClass().getResourceAsStream(
                        "/au/edu/murdoch/ccg/baat.dtd"
                    );
                    logger.info("using local baat.dtd");
                    return new InputSource( in );
                }
            };

            SAXReader xmlReader = new SAXReader(false);
            xmlReader.setEntityResolver(resolver);
            baatFile = xmlReader.read(toolFile); //throws DocumentException on a parse error

            //load the toolpath
            Element jobNode = (Element) baatFile.selectSingleNode("//job");
            if (jobNode != null) {
                this.toolPath = jobNode.attributeValue("toolPath");
            }

            //load the outputFiletypes tag
            Element outputFiletypesNode = (Element) baatFile.selectSingleNode("//outputFiletypes");
            if (outputFiletypesNode != null) {
                String sod = outputFiletypesNode.attributeValue("symlinkOutputDir");
                if (sod == null) {
                    this.symlinkOutputDir = false;
                } else if (sod.compareTo("true") == 0){
                    this.symlinkOutputDir = true;
                }
            }

            //load the parameters as per the baat file
            XPath xpathSelector = DocumentHelper.createXPath("//parameter");
            List results = xpathSelector.selectNodes(baatFile);
            for ( Iterator iter = results.iterator(); iter.hasNext(); ) {
                Element element = (Element) iter.next();
                //convert to a BaatParameter class and add to ArrayList
                BaatParameter bp = new BaatParameter();
                bp.switchName = element.attributeValue("switch");
                bp.rank = element.attributeValue("rank");
                bp.switchUse = element.attributeValue("switchUse");
                bp.mandatory = element.attributeValue("mandatory"); 
                bp.filter = element.attributeValue("filter");
                if (bp.filter == null) {
                    bp.filter = "";
                }
                bp.sourceParam = element.attributeValue("sourceParam");
                if (bp.sourceParam == null) {
                    bp.sourceParam = "";
                }
                bp.appendString = element.attributeValue("appendString");
                if (bp.appendString == null) {
                    bp.appendString = "";
                }
                bp.extensionParameter = element.attributeValue("extensionParam");
                if (bp.extensionParameter == null) {
                    bp.extensionParameter = "";
                }
                bp.inputFile = element.attributeValue("inputFile");
                bp.value = element.attributeValue("value");
                if (element.attributeValue("value") != null &&
                    element.attributeValue("value").length() > 0) {
                    bp.isSet = true; //pretend values are set when a default is specified in the baat
                }
                if (element.attributeValue("outputFile") != null) {
                    bp.outputFile = element.attributeValue("outputFile");
                }
                bp.primaryExtension = element.attributeValue("primaryExtension");
   
                //if inputFile = 'yes' then search for out/inputExtension subelements
                if (bp.inputFile.compareTo("yes") == 0) {
                    ArrayList outputExtensions = new ArrayList();
                    ArrayList inputExtensions = new ArrayList();
                    List extResults = element.elements();
                    for ( Iterator xiter = extResults.iterator(); xiter.hasNext(); ) {
                        Element xelem = (Element) xiter.next();
                        String extension = xelem.getText();
                        if (xelem.getName().compareTo("outputExtension") == 0) {
                            outputExtensions.add(extension);
                        }
                        else if (xelem.getName().compareTo("inputExtension") == 0) {
                            inputExtensions.add(extension);
                        }
                    }
                    if (outputExtensions.size() > 0) {
                        bp.outputExtensions = outputExtensions;
                    }
                    if (inputExtensions.size() > 0) {
                        bp.inputExtensions = inputExtensions;
                    }
                }

                parameters.add(bp);
            }
        } else {
            throw new Exception("toolName not specified. Could not load tool definition");
        }
    }

    public void setParameter(String switchName, String value) {
        setParameter(null, switchName, value);
    }

    public void addInputFile(String filename) {
        if (filename.length() > 1 &&
            ! this.inputFiles.contains(filename) ) {
            this.inputFiles.add(filename);
        }
    }

    public void addInputFiles(String[] filenames) {
        for (int i=0; i<filenames.length;i++) {
            this.addInputFile(filenames[i]);
        }
    }

    public void setParameter(String rank, String switchName, String value) {
        //iterate over parameters until we find the switchName or a matching rank
        Iterator iter = parameters.iterator();
        while (iter.hasNext()) {
            BaatParameter bp = (BaatParameter) iter.next();
            if (    ( rank != null && rank.compareTo(bp.rank) == 0 ) ||
                    ( bp.switchName.compareTo(switchName) == 0 ) ) { //allow matching by rank, but fallback to name

                //skip empty
                if (value == null || value.length() == 0) {
                    continue;
                }

                bp.value = value;
                bp.isSet = true;
                
                if (bp.inputFile.compareTo("yes") == 0 && value.length() > 0) {
                    //add this value to the inputFiles list
                    inputFiles.add(value);

                    //if there is a 'removePath' filter, remove anything that looks like a path from the value
                    if (bp.filter != null && bp.filter.equalsIgnoreCase("removePath")) {
                        int lastPath = bp.value.lastIndexOf("/");
                        int filenameIndex = lastPath + 1;
                        if (filenameIndex < 0 || lastPath >= bp.value.length()) {
                            filenameIndex = 0;
                        }
                        bp.value = bp.value.substring(filenameIndex);
                    }

                    if ( bp.outputExtensions.size() > 0) {
                        //add output filenames to the arraylist
                        for (Iterator outiter = bp.outputExtensions.iterator(); outiter.hasNext(); ) {
                            String extension = (String) outiter.next();
                            //TODO strip everything except the actual filename if there is anything else (?)
                            String newFileName = value + "." + extension;
                            outputFiles.add(newFileName);
                        }
                    }
                    if ( bp.inputExtensions.size() > 0) {
                        //add input filenames to the arraylist
                        for (Iterator initer = bp.inputExtensions.iterator(); initer.hasNext(); ) {
                            String extension = (String) initer.next();
                            //TODO strip everything except the actual filename if there is anything else (?)
                            String newFileName = value + "." + extension;
                            inputFiles.add(newFileName);
                        }
                    }
                }
                if (bp.outputFile.compareTo("yes") == 0) {
                    outputFiles.add(value);
                }
            } 
        }
    }

    public String getPrimaryExtension(String switchName) {
        //iterate over parameters until we find the switchName 
        Iterator iter = parameters.iterator();
        while (iter.hasNext()) {
            BaatParameter bp = (BaatParameter) iter.next();
            if (  bp.switchName.compareTo(switchName) == 0  ) { 
                return bp.primaryExtension; //could be null, usually is
            }   
        }   
        return null;
    }

    public String getToolPath () {
        return this.toolPath;
    }

    public String getCommandLine() throws CBBCException {
        String command = this.toolPath + " ";

        this.validateParameters(); //throws CBBCException

        //append all parameters to the end
        //TODO do this in a particular order
        Iterator iter = this.parameters.iterator();
        while (iter.hasNext()) {
            BaatParameter bp = (BaatParameter) iter.next();

            String tempValue = bp.value;

            if (bp.filter != null && bp.filter.equalsIgnoreCase("prependRootDir")) {
                tempValue = rootDir + bp.value;
            } else if (bp.filter != null && bp.filter.equalsIgnoreCase("prependUserDir")) {
                tempValue = rootDir + username + "/" + bp.value;
            } else if (bp.filter != null && bp.filter.equalsIgnoreCase("../../")) {
                tempValue = "../../" + bp.value;
            }

            if (bp.switchUse.equalsIgnoreCase("both")) {
                command += bp.switchName + " " + tempValue + " ";
            } else if (bp.switchUse.equalsIgnoreCase("valueOnly")) {
                command += tempValue + " ";
            } else if (bp.switchUse.equalsIgnoreCase("switchOnly")) {
                command += bp.switchName + " ";
            }
        }
    
        return command;
    }

    //use this method to pre-fill parameters that derive their value from another input parameter
    //called before validation
    public void setSourceParams() {
        Iterator iter = this.parameters.iterator();
        
        while (iter.hasNext()) {
            BaatParameter bpDest = (BaatParameter) iter.next();
            String sourceValue = null; //the source param value
            String extensionParameterValue = null;//the source for our extension, if the option is set
            
            if (bpDest.sourceParam != null && bpDest.sourceParam.compareTo(bpDest.switchName) != 0) {
                Iterator reiter = this.parameters.iterator(); //yep, we're looping twice over the same variables
                while (reiter.hasNext()) {
                    BaatParameter bpSrc = (BaatParameter) reiter.next();
                    if (bpSrc.switchName.compareTo(bpDest.sourceParam) == 0) {
                        //located the root source param
                        sourceValue = bpSrc.value;
                    }
                    if (bpDest.extensionParameter != null && bpDest.extensionParameter.compareTo(bpSrc.switchName) == 0) {
                        //located the source of the extension
                        extensionParameterValue = bpSrc.value;
                    }
                }
                
                if (sourceValue != null) {
                    //we've found the source from which we hope to derive our value
                    bpDest.value = sourceValue;
                    bpDest.isSet = true;
                    if (bpDest.appendString != null && bpDest.appendString.compareTo("") != 0) {
                        bpDest.value += bpDest.appendString;
                    }
                    if (extensionParameterValue != null) {
                        bpDest.value += "." + extensionParameterValue;
                    }
                    logger.info("derived input param from source param: ["+bpDest.switchName+":"+bpDest.value+"]");
                }
                
            }
        }
    }
    
    public void validateParameters() throws CBBCException {
        reconcileParams();

        Iterator iter = this.parameters.iterator();
        while (iter.hasNext()) {
            BaatParameter bp = (BaatParameter) iter.next();
            String switchUse = bp.switchUse;
            String switchValue = bp.value;
            String switchString = bp.switchName;

            //skip unset params
            if (!bp.isSet) {
                continue;
            }

            // determine switch use
            if (switchUse.equalsIgnoreCase("both")) {
                // dont really need to do anything, perhaps make sure both are set
                if (switchValue == null || switchValue.length() == 0) {
                    throw new CBBCException("Switch use 'both' is set but no value provided: "+switchString);
                }
                if (switchString == null || switchString.length() == 0) {
                    throw new CBBCException("Switch use 'both' is set but no switch provided: "+switchString);
                }
            } else if (switchUse.equalsIgnoreCase("valueOnly")) {
                if (switchValue == null || switchValue.length() == 0) {
                    throw new CBBCException("Value only is set but no value provided: "+switchString);
                }
                switchString = null;
            } else if (switchUse.equalsIgnoreCase("switchOnly")) {
                if (switchString == null || switchString.length() == 0) {
                    throw new CBBCException("Switch only is set but no switch provided: "+switchString);
                }
                switchValue = null;
            } else if (switchUse.equalsIgnoreCase("combined")) {
                if (switchValue == null || switchValue.length() == 0) {
                    throw new CBBCException("Switch use 'both' is set but no value provided: "+switchString);
                }
                if (switchString == null || switchString.length() == 0) {
                    throw new CBBCException("Switch use 'both' is set but no switch provided: "+switchString);
                }
                switchString += switchValue;
                switchValue = null;
            } else {
                throw new CBBCException("Expected attribute 'switchUse' invalid, value [" + switchUse + "]: "+switchString);
            }
        }
    }

    public static void main(String[] args) {
        try {

            System.out.println("TEST 1:repeatmasker");
            BaatInstance bi = new BaatInstance("repeatmasker");
            bi.setParameter("1","","datafile.txt");
            System.out.println("baat has inputfiles: " + bi.getInputFiles());
            System.out.println("baat has outputfiles: " + bi.getOutputFiles());
            System.out.println("XML:\n"+bi.exportXML());

            System.out.println("TEST 2: blast");
            bi = new BaatInstance("blast");
            bi.setParameter("-i","datafile.txt");
            bi.setParameter("-o","output.txt");
            System.out.println("baat has inputfiles: " + bi.getInputFiles());
            System.out.println("baat has outputfiles: " + bi.getOutputFiles());
            System.out.println("XML:\n"+bi.exportXML());

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}

class BaatParameter {
    public String rank = "";
    public String switchUse = "";
    public String switchName = "";
    public String mandatory = "";
    public String filter = "";
    public String inputFile = "";
    public String outputFile = "";
    public String value = "";
    public ArrayList outputExtensions;
    public ArrayList inputExtensions;
    public String primaryExtension = "";
    public String sourceParam = ""; //used where a parameter value is derived from another parameter's setting
    public String appendString = ""; //used as an appender when a sourceParam is used 
    public String extensionParameter = ""; //used with sourceParam allows another parameter to be used as the extension for this parameter
    public boolean isSet = false; //manually mark this when setting a value

    public BaatParameter() {
        outputExtensions = new ArrayList();
        inputExtensions = new ArrayList();
    }
}
