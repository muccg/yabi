package au.edu.murdoch.ccg.yabi.util;

import org.apache.axis.soap.*;
import javax.xml.soap.*;
import java.util.*;
import java.net.*;
import java.io.*;
import javax.activation.DataHandler;

public class SoapTest {

    public static void main (String[] args) {
        try {
            BufferedReader br = new BufferedReader(new FileReader("../../sample-baat.xml"));
            String xmlString = "";
            String line = "";
            while ( (line = br.readLine()) != null) {
                xmlString += line;
            }

            String[] attachments = new String[1];
            attachments[0] = "file:///export/home/tech/ntakayama/devel/ccg/yabi-mw/DQ6060.zip";
            long jobId = GrendelClient.submitXMLJob(xmlString, attachments);

            System.out.println("jobId : " + jobId);

        } catch (Exception e) {
            System.out.println(e.getClass() + " : " + e.getMessage());
            e.printStackTrace();
        }

    }

}
