package au.edu.murdoch.ccg.yabi.util;

import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import org.apache.commons.configuration.*;
import java.io.*;
import java.util.*;

public class FileParamExpander {

    private String yabiRootDir;
    private String username;

    public FileParamExpander() {
        try {
            //load config details
            Configuration conf = YabiConfiguration.getConfig();
            this.yabiRootDir = conf.getString("yabi.rootDirectory");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void setUsername(String username) {
        this.username = username;
    }

    /**
     * expandString
     * 
     * takes in a single string and splits it on commas
     * then looks at each item and assesses if it is a zip file or directory within the user's data directory
     * if a zip, unzips it to a subdir and expands on the subir
     * if a subdir, expands the subdir out to individual files
     * @returns String[] separatedFiles
     */
    public String[] expandString(String param) {
        String[] tokenized = param.split(",");
        ArrayList expanded = new ArrayList();

        //if the string was empty, then return an empty array rather than expanding out the user's directory in its entirety
        if (param.length() < 1) {
            return tokenized;
        }

        for (int i=0;i < tokenized.length;i++) {
            //first, check for zippiness
            if (tokenized[i].endsWith(".zip")) {
                System.out.println("fileParamExpander: zip file: "+tokenized[i]);
                try {
                    expanded.addAll(Zipper.unzip(this.yabiRootDir + this.username + "/" + tokenized[i], this.yabiRootDir + this.username, "data", true));
                } catch (Exception e) {
                    e.printStackTrace();
                }
            } else {
                File possibleFile =  new File(this.yabiRootDir + this.username + "/", tokenized[i]);
                if (!possibleFile.exists()) {
                    //maybe this isn't a file reference?
                    //add to final array just in case
                    expanded.add(tokenized[i]);
                    System.out.println("fileParamExpander: file not found: "+tokenized[i]);
                    continue;
                }
                if (possibleFile.isDirectory()) {
                    System.out.println("fileParamExpander: directory: "+tokenized[i]);
                    String[] dirExpansion = possibleFile.list();
                    for (int j=0;j < dirExpansion.length; j++) {
                        //expand directories out one level only
                        System.out.println("fileParamExpander: dirExpanded: "+tokenized[i]+"/"+dirExpansion[j]);
                        expanded.add(tokenized[i]+"/"+dirExpansion[j]);
                    }
                    continue;
                }
                //if we fall through here, it is probably a straight file reference
                System.out.println("fileParamExpander: file: "+tokenized[i]);
                expanded.add(tokenized[i]);
            }
            
        }

        //now repackage as final String[] and return
        Iterator iter = expanded.iterator();
        String[] repackaged = new String[expanded.size()];
        int i = 0;
        while(iter.hasNext()) {
            repackaged[i++] = (String) iter.next();
        }

        return repackaged;
    }

}
