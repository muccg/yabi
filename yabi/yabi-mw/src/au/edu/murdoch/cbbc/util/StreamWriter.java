package au.edu.murdoch.cbbc.util;

/**
 * $Id: StreamWriter.java,v 1.1 2003/09/16 10:36:36 a.hunter Exp $
 *
 * Adam Hunter (a.hunter@cbbc.murdoch.edu.au)
 *
 * $Log: StreamWriter.java,v $
 * Revision 1.1  2003/09/16 10:36:36  a.hunter
 * Library code. Sucked from other (the project formerly known as legumedb)
 * projects. Will build a db & util jar.
 *
 * Revision 1.2  2002/12/04 04:42:22  a.hunter
 * *** empty log message ***
 *
 * Revision 1.1.1.1  2002/07/09 04:07:06  a.hunter
 * Imported legumedb project
 *
 * Revision 1.1  2002/05/07 10:44:40  a.hunter
 * Created.
 *
 */

import java.io.*;

import org.apache.log4j.Logger;

public class StreamWriter extends Thread {

    /**
     * logger
     */
    private static Logger logger = Logger.getLogger(StreamWriter.class);

    /**
     * Size of read buffer
     */
    public static final int BUFFER_SIZE = 4096;

    /**
     * Input stream
     */
    BufferedInputStream bis = null;

    /**
     * File to write to
     */
    FileOutputStream fileWriter = null;

    /**
     * File name
     */
    private String filename = null;


    /**
     * Constructor
     */
    public StreamWriter() {
        setPriority(Thread.MAX_PRIORITY);
    }


    /**
     * Record
     */
    public void record(InputStream is, String str) throws CBBCException {
        try {
            bis = new BufferedInputStream(is);
            filename = str;
            start();
        } catch (Throwable t) {
            throw new CBBCException(t);
        }
    }


    /**
     * Constructor
     */
    public StreamWriter(InputStream is, String str) throws CBBCException {
        record(is, str);
    }


    /**
     * Run
     */
    public void run() {
        try {
            byte[] buffer = new byte[BUFFER_SIZE];
            int bytesRead = 0;
            bytesRead = bis.read(buffer, 0, BUFFER_SIZE);

            if (bytesRead != -1) {
                fileWriter = new FileOutputStream(new File(filename));
            }

            while (bytesRead != -1) {
                fileWriter.write(buffer, 0, bytesRead);
                bytesRead = bis.read(buffer, 0, BUFFER_SIZE);
            }

            if (bis != null) {
                bis.close();
            }
            if (fileWriter != null) {
                fileWriter.close();
            }
        } catch (Throwable t) {
            //try {
            //    insertResult(t.getClass().getName(), ResultHandler.FILE_TYPE_ERROR, t.getMessage() + " \n " + StringUtil.printStackTrace(t));
            //} catch (ToolRunnerException tre) {
            logger.error(t.getMessage(), t);
        }
    }
}

