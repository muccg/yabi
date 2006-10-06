package au.edu.murdoch.ccg.yabi.util;

import java.io.*;
import java.util.zip.*;
import java.util.*;

public abstract class Zipper {

    public static void createZipFile (String outFilename, String tempDir, ArrayList files) throws Exception {
        // Create a buffer for reading the files
        byte[] buf = new byte[1024];
    
        // Create the ZIP file
        ZipOutputStream out = new ZipOutputStream(new FileOutputStream(tempDir + outFilename));

        Iterator iter = files.iterator();
        while (iter.hasNext()) {
            String filename = (String) iter.next();
    
            FileInputStream in = new FileInputStream(tempDir + filename);
   
            // Add ZIP entry to output stream.
            out.putNextEntry(new ZipEntry(filename));
    
            // Transfer bytes from the file to the ZIP file
            int len;
            while ((len = in.read(buf)) > 0) {
                out.write(buf, 0, len);
            }
    
            // Complete the entry
            out.closeEntry();
            in.close();
        }
    
        // Complete the ZIP file
        out.close();
    }

}
