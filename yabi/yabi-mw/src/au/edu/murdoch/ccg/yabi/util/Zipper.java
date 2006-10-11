package au.edu.murdoch.ccg.yabi.util;

import java.io.*;
import java.util.zip.*;
import java.util.*;
import java.net.*;

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

    public static void unzip (String inFilename, String destination) throws Exception {
        ZipFile zipFile;
        Enumeration entries;
        //destination should be a directory name with trailing slash
        File destCheck = new File(destination);
        if (! destCheck.exists()) {
            throw new Exception("destination directory does not exist: "+destination);
        }
        if (! destination.endsWith("/")) {
            destination = destination + "/";
        }

        try {   
            zipFile = new ZipFile(inFilename);
            
            entries = zipFile.entries();
            
            while(entries.hasMoreElements()) {
                ZipEntry entry = (ZipEntry)entries.nextElement();
            
                if(entry.isDirectory()) {
                    // Assume directories are stored parents first then children.
                    System.err.println("Extracting directory: " + entry.getName());
                    // This is not robust, just for demonstration purposes.
                    (new File(entry.getName())).mkdir();
                    continue;
                }   
            
                System.err.println("Extracting file: " + entry.getName());
                copyInputStream(zipFile.getInputStream(entry), new BufferedOutputStream(new FileOutputStream(destination + entry.getName())));
            } 
    
            zipFile.close();
        } catch (IOException ioe) {
            System.err.println("Unhandled exception:");
            ioe.printStackTrace();
            System.err.println(inFilename);
            return;
        }
    }

    public static void unzip (URL source, String destination) throws Exception {
        String fname = source.getFile(); //unfortunately this includes the directories
        fname = fname.substring( fname.lastIndexOf( System.getProperty("file.separator") ) + 1 );
        String localSource = destination + fname;

        //download the file locally before unzipping
        FileOutputStream fos = new FileOutputStream(localSource);
        InputStream is = source.openStream();
        copyInputStream(is, fos);

        //unzip!
        unzip(localSource, destination);
    }

    private static final void copyInputStream(InputStream in, OutputStream out) throws IOException {
        byte[] buffer = new byte[1024];
        int len;

        while((len = in.read(buffer)) >= 0)
            out.write(buffer, 0, len);

        in.close();
        out.close();
    }

}
