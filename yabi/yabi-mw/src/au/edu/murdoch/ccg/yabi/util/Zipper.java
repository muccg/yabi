package au.edu.murdoch.ccg.yabi.util;

import java.io.*;
import java.util.zip.*;
import java.util.*;
import java.net.*;

public abstract class Zipper {

    public static void createZipFile (String outFilename, String tempDir, String username, ArrayList files) throws Exception {
        // Create a buffer for reading the files
        byte[] buf = new byte[1024];
    
        // Create the ZIP file
        ZipOutputStream out = new ZipOutputStream(new FileOutputStream(tempDir + outFilename));

        //first, expand out the indicidual components to ensure we don't have any directories etc
        FileParamExpander fpe = new FileParamExpander();
        fpe.setUsername(username);
        Iterator iter = files.iterator();
        ArrayList expandedFiles = new ArrayList();
        while (iter.hasNext()) {
            String[] filesArray = fpe.expandString( (String) iter.next() );
            for (int i=0; i< filesArray.length;i++) {
                expandedFiles.add(filesArray[i]);
            }
        }

        HashMap dupCheck = new HashMap();

        iter = expandedFiles.iterator();
        while (iter.hasNext()) {
            String filename = (String) iter.next();
            if (dupCheck.containsKey(filename)) {
                continue;
            }

            dupCheck.put(filename, "true");    

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

    public static ArrayList unzip (String inFilename, String destination, String prefix) throws Exception {
        return unzip(inFilename, destination, prefix, false);
    }

    public static ArrayList unzip (String inFilename, String destination, String prefix, boolean withDirs) throws Exception {
        ZipFile zipFile;
        Enumeration entries;
        ArrayList fileList = new ArrayList();

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

            //create directory using 'prefix' as the name
            String dataDirLoc = destination + prefix;
            File dataDir = new File(dataDirLoc);
            if (!dataDir.exists()) {
                dataDir.mkdir();
            }
            
            while(entries.hasMoreElements()) {
                ZipEntry entry = (ZipEntry)entries.nextElement();
            
                if (! entry.getName().startsWith(".") && !entry.getName().startsWith("__MACOSX")) {

                    if(entry.isDirectory()) {
                        if (withDirs) {
                            // Assume directories are stored parents first then children.
                            //System.err.println("Extracting directory: " + entry.getName());
                            // This is not robust, just for demonstration purposes.
                            (new File(dataDir, entry.getName())).mkdir();
                        }
                        continue;
                    }   
            
                    String entryName = entry.getName();
                    if (!withDirs) {
                        int prunePoint = entryName.lastIndexOf("/") + 1;
                        if (prunePoint <= 0 || prunePoint >= entryName.length() - 1) {
                            prunePoint = 0;
                        } 
                        entryName = entryName.substring(prunePoint);
                    } 
                    //System.err.println("Extracting file: " + entryName);
                    copyInputStream(zipFile.getInputStream(entry), new BufferedOutputStream(new FileOutputStream(destination + prefix + "/" + entryName)));
                    fileList.add(entryName);
                }
            } 
    
            zipFile.close();
        } catch (IOException ioe) {
            System.err.println("Unhandled exception:");
            ioe.printStackTrace();
            System.err.println(inFilename);
        }

        return fileList;
    }

    public static void unzip (URL source, String destination) throws Exception {
        unzip(source, destination, "");
    }

    public static void unzip (URL source, String destination, String prefix) throws Exception {
        String fname = source.getFile(); //unfortunately this includes the directories
        fname = fname.substring( fname.lastIndexOf( System.getProperty("file.separator") ) + 1 );
        String localSource = destination + fname;

        //download the file locally before unzipping
        FileOutputStream fos = new FileOutputStream(localSource);
        InputStream is = source.openStream();
        copyInputStream(is, fos);

        //unzip!
        unzip(localSource, destination, prefix);

        //del zip file
        File doomed = new File(localSource);
        doomed.delete();
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
