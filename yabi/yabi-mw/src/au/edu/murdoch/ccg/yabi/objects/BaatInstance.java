package au.edu.murdoch.ccg.yabi.objects;

import org.dom4j.*; 
import java.util.*;
import java.io.*;
import org.dom4j.io.*;
import java.net.*;

public class BaatInstance {

    private static final String toolDefinitionDirectory = "http://ccg.murdoch.edu.au/jobs/xml/tools/";

    private String toolName;
    private ArrayList parameters;
    private ArrayList inputFiles;
    private ArrayList outputFiles;
    private Document baatFile;
    private String attachedFile;

    public BaatInstance(String toolName) throws Exception {
        //init vars
        this.toolName = toolName.replaceAll(System.getProperty("file.separator"), ""); //remove directory separators to prevent hacks

        parameters = new ArrayList();
        inputFiles = new ArrayList();
        outputFiles = new ArrayList();

        //load Baat XML for use in validating and identifying input and output files
        loadBaat();
    }

    public ArrayList getParameters() {
        return this.parameters;
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

    public void setAttachedFile(String fileLoc) {
        this.attachedFile = fileLoc;
    }

    public String exportXML() {
        //process the contents of this Baat and convert to the simplest XML output that can be used by Grendel, for instance
        
        //call to strip out unused params
        reconcileParams();

        return baatFile.asXML();
    }

    private void reconcileParams() {
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

        if (attachedFile.length() > 0) {
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
        submitUserNode.setText( "some user" );

        Element submitLabel = (Element) baatFile.selectSingleNode("//submitLabel");
        submitLabel.setText( "some_random_label" );

    }

    private void loadBaat() throws Exception {
        if (toolName != null) {
            String toolFileName = toolDefinitionDirectory + toolName + ".xml";
            URL toolFile = new URL(toolFileName);
            SAXReader xmlReader = new SAXReader();
            baatFile = xmlReader.read(toolFile); //throws DocumentException on a parse error

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
                bp.inputFile = element.attributeValue("inputFile");
                bp.value = element.attributeValue("value");
                if (element.attributeValue("outputFile") != null) {
                    bp.outputFile = element.attributeValue("outputFile");
                }
   
                //if inputFile = 'yes' then search for outputExtension subelements
                if (bp.inputFile.compareTo("yes") == 0) {
                    ArrayList outputExtensions = new ArrayList();
                    List extResults = element.elements();
                    for ( Iterator xiter = extResults.iterator(); xiter.hasNext(); ) {
                        Element xelem = (Element) xiter.next();
                        String extension = xelem.getText();
                        outputExtensions.add(extension);
                    }
                    if (outputExtensions.size() > 0) {
                        bp.outputExtensions = outputExtensions;
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

    public void setParameter(String rank, String switchName, String value) {
        //iterate over parameters until we find the switchName or a matching rank
        Iterator iter = parameters.iterator();
        while (iter.hasNext()) {
            BaatParameter bp = (BaatParameter) iter.next();
            if (    ( rank != null && rank.compareTo(bp.rank) == 0 ) ||
                    ( bp.switchName.compareTo(switchName) == 0 ) ) { //allow matching by rank, but fallback to name
                bp.value = value;
                bp.isSet = true;
                
                if (bp.inputFile.compareTo("yes") == 0) {
                    //add this value to the inputFiles list
                    inputFiles.add(value);

                    if ( bp.outputExtensions.size() > 0) {
                        //add output filenames to the arraylist
                        for (Iterator outiter = bp.outputExtensions.iterator(); outiter.hasNext(); ) {
                            String extension = (String) outiter.next();
                            //TODO strip everything except the actual filename if there is anything else (?)
                            String newFileName = value + "." + extension;
                            outputFiles.add(newFileName);
                        }
                    }
                }
                if (bp.outputFile.compareTo("yes") == 0) {
                    outputFiles.add(value);
                }
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
    public String inputFile = "";
    public String outputFile = "";
    public String value = "";
    public ArrayList outputExtensions;
    public boolean isSet = false; //manually mark this when setting a value

    public BaatParameter() {
        outputExtensions = new ArrayList();
    }
}
