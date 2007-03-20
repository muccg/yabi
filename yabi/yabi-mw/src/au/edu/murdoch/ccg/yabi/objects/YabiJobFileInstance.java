package au.edu.murdoch.ccg.yabi.objects;

import org.dom4j.*; 
import org.dom4j.tree.*;
import java.util.*;
import java.io.*;
import org.dom4j.io.*;
import java.net.*;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import org.apache.commons.configuration.*;

public class YabiJobFileInstance {

    private static String yabiRootDirectory;

    private Document jobFile;
    private String fileName;

    public YabiJobFileInstance(String fileName) throws Exception {
        //init vars
        //this.fileName = fileName.replaceAll(System.getProperty("file.separator"), ""); //remove directory separators to prevent hacks
        this.fileName = fileName.replaceAll(" ","_"); //remove spaces and replace with underscores

        //load config
        Configuration config = YabiConfiguration.getConfig();
        yabiRootDirectory = config.getString("yabi.rootDirectory");

        loadFile();
    }

    public YabiJobFileInstance() throws Exception {
        //load config
        Configuration config = YabiConfiguration.getConfig();
        yabiRootDirectory = config.getString("yabi.rootDirectory");
    }

    public void initFromString(String xml) throws DocumentException {
        StringReader sr = new StringReader(xml);
        SAXReader xmlReader = new SAXReader();
        jobFile = xmlReader.read(sr); //throws DocumentException on a parse error
    }

    // ---- GETTING CONTENTS ----

    public String getJobName() {
        if (this.jobFile != null) {
            Element jobName = (Element) this.jobFile.selectSingleNode("//jobName");
            if (jobName != null) return jobName.getText();
        }
        return null;
    }

    public String getUserName() {
        if (this.jobFile != null) {
            Element userName = (Element) this.jobFile.selectSingleNode("//userName");
            if (userName != null)  return userName.getText();
        }
        return null;
    }

    public String getYear() {
        if (this.jobFile != null) {
            Element year = (Element) this.jobFile.selectSingleNode("//year");
            if (year != null) return year.getText();
        }
        return null;
    }

    public String getMonth() {
        if (this.jobFile != null) {
            Element month = (Element) this.jobFile.selectSingleNode("//month");
            if (month != null) return month.getText();
        }
        return null;
    }

    public String getStartTime() {
        if (this.jobFile != null) {
            Element startTime = (Element) this.jobFile.selectSingleNode("//startTime");
            if (startTime != null) return startTime.getText();
        }
        return null;
    }

    public String getEndTime() {
        if (this.jobFile != null) {
            Element endTime = (Element) this.jobFile.selectSingleNode("//endTime");
            if (endTime != null) return endTime.getText();
        }
        return null;
    }

    public String getVariableByKey(String key) {
        if (this.jobFile != null) {
            Element varElem = (Element) this.jobFile.selectSingleNode("//variable[@key='" + key + "']");
            if (varElem != null) {
                return varElem.attributeValue("value");
            }
        }
        return null;
    }

    public String getProcessDefinition() {
        if (this.jobFile != null) {
            Element pdElem = (Element) this.jobFile.selectSingleNode("//process-definition");
            if (pdElem != null) {
                return pdElem.asXML();
            }
        }
        return null;
    }

    public Map getVariables() {
        HashMap vars = new HashMap();
        if (this.jobFile != null) {
            XPath xpathSelector = DocumentHelper.createXPath("//variable");
            List results = xpathSelector.selectNodes(jobFile);
            for ( Iterator iter = results.iterator(); iter.hasNext(); ) {
                Element element = (Element) iter.next();

                String key = element.attributeValue("key");
                String value = element.attributeValue("value");

                vars.put(key, value);
            }
        }
        return vars;
    }

    // ---- MODIFYING CONTENTS ----

    public void setJobName(String input) {
        if (this.jobFile != null) {
            Element jobName = (Element) this.jobFile.selectSingleNode("//jobName");
            jobName.setText(input);
        }
    }

    public void setStartTime(String input) {
        if (this.jobFile != null) {
            Element startTime = (Element) this.jobFile.selectSingleNode("//startTime");
            if (startTime == null) {
                startTime = new DefaultElement("startTime");
                Element yabiJobNode = (Element) this.jobFile.selectSingleNode("//yabi-job");
                startTime.setText(input);
                yabiJobNode.add(startTime);
            } else {
                startTime.setText(input);
            }
        }
    }

    public void setEndTime(String input) {
        if (this.jobFile != null) {
            Element endTime = (Element) this.jobFile.selectSingleNode("//endTime");
            if (endTime == null) {
                endTime = new DefaultElement("endTime");
                Element yabiJobNode = (Element) this.jobFile.selectSingleNode("//yabi-job");
                endTime.setText(input);
                yabiJobNode.add(endTime);
            } else {
                endTime.setText(input);
            }

        }
    }

    public void setVariableForKey(String key, String value) {
        if (this.jobFile != null) {
            Element varElem = (Element) this.jobFile.selectSingleNode("//variable[@key='" + key + "']");
            if (varElem == null) { //add node as it doesn't exist
                Element variablesElem = (Element) this.jobFile.selectSingleNode("//variables");
                varElem = new DefaultElement("variable");
                varElem.addAttribute("key", key);
                varElem.addAttribute("value", value);
                try {
                    variablesElem.add(varElem);
                } catch (IllegalAddException e) {}
            } else {
                varElem.addAttribute("key", key);
                varElem.addAttribute("value", value);
            }
        }
    }

    public void insertVariableMap(Map vars) {
        if (vars != null) {
            Iterator iter = vars.keySet().iterator();
            while (iter.hasNext()) {
                String key = (String) iter.next();
                this.setVariableForKey(key, (String)vars.get(key));
                //System.out.println("setting ["+key+"] = ["+vars.get(key)+"]");
            }
        }
    }

    // ---- FILE LOAD/SAVE METHODS ----

    private void loadFile() throws Exception {
        if (fileName != null) {
            String fileLoc = yabiRootDirectory + fileName;
            File file = new File(fileLoc);
            SAXReader xmlReader = new SAXReader();
            jobFile = xmlReader.read(file); //throws DocumentException on a parse error

        } else {
            throw new Exception("File not specified");
        }
    }

    public void saveFile() throws Exception {
        this.saveFile(null);
    }

    public void saveFile(String toLocation) throws Exception {
        if (toLocation != null) {
            fileName = toLocation;
        }

        if (fileName != null) {
            String fileLoc = yabiRootDirectory + fileName;
            FileWriter fw = new FileWriter( fileLoc );
            OutputFormat of = new OutputFormat("  ");
            of.setNewlines(true);
            of.setTrimText(true);
            XMLWriter xmlw = new XMLWriter( fw , of );

            xmlw.write(jobFile);

            xmlw.close();

        } else {
            throw new Exception("File not specified");
        }
    }

}
