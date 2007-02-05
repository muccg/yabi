package au.edu.murdoch.ccg.yabi.objects;

import org.dom4j.*; 
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
        this.fileName = fileName;

        //load config
        Configuration config = YabiConfiguration.getConfig();
        yabiRootDirectory = config.getString("yabi.rootDirectory");

        loadFile();
    }

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
        if (fileName != null) {
            String fileLoc = yabiRootDirectory + fileName + ".modified";
            FileWriter fw = new FileWriter( fileLoc );
            XMLWriter xmlw = new XMLWriter( fw );

            xmlw.write(jobFile);

            xmlw.close();

        } else {
            throw new Exception("File not specified");
        }
    }

    public static void main(String[] args) {
        try {

            String fname = "/tmp/ntakayama/yabi-jobs/ntakayama/jobs/somewhere.jobxml";
            YabiJobFileInstance yjfi = new YabiJobFileInstance(fname);
            yjfi.saveFile();

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
