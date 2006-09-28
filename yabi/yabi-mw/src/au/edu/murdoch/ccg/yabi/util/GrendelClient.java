package au.edu.murdoch.ccg.yabi.util;

import org.apache.axis.soap.*;
import javax.xml.soap.*;
import java.util.*;
import java.net.*;
import java.io.*;
import javax.activation.DataHandler;

public class GrendelClient {

    public static String grendelUrl = "http://grendel.localdomain:8080/axis-1_2_1/services/grendel";

    public static long submitXMLJob (String xmlString, String[] attachments) throws Exception {
        //create SOAP message
        MessageFactory factory = MessageFactory.newInstance();
        SOAPMessage message = factory.createMessage();

        //defined our body as a submitXMLJob call
        SOAPBody body = message.getSOAPBody();
        SOAPFactory soapFactory = SOAPFactory.newInstance();
        Name bodyName = soapFactory.createName("submitXMLJob", "", "urn:Grendel");
        SOAPBodyElement bodyElement = body.addBodyElement(bodyName); 
    
        //add out xmlString as an argument
        Name name = soapFactory.createName("task");
        SOAPElement xmlStringElem = bodyElement.addChildElement(name);
        xmlStringElem.addTextNode(xmlString); 

        //prepare to make connection to grendel
        SOAPConnectionFactory soapConnectionFactory = SOAPConnectionFactory.newInstance();
        SOAPConnection connection = soapConnectionFactory.createConnection();
      
        java.net.URL endpoint = new URL(grendelUrl);

        //add attachments
        if (attachments != null) {
            for (int i = 0; i < attachments.length; i++ ) {
                try {
                    URL url = new URL(attachments[i]);
                    DataHandler dataHandler = new DataHandler(url);
                    AttachmentPart attachment = message.createAttachmentPart(dataHandler);
                    attachment.setContentId("attached_file");

                    message.addAttachmentPart(attachment);
                } catch (Exception e) {
                    //ignore faulty files
                }
            }
        }

            //debug
            System.out.println("SENDING");
            message.writeTo(System.out);
            System.out.println("--------");

        //make the SOAP call
        SOAPMessage response = connection.call(message, endpoint);

        //examine response
        SOAPHeader header = response.getSOAPHeader();
        SOAPBody rbody = response.getSOAPBody();

        //check for a fault
        if ( rbody.hasFault() ) {

            SOAPFault newFault = rbody.getFault();
            Name code = newFault.getFaultCodeAsName();
            String string = newFault.getFaultString();

            connection.close();

            throw new Exception(string);

        } else {

            //fetch grendel ID from response
            //this number is stored in the following hierarchy
            //<Body><submitXMLJobResponse><submitXMLJobReturn>0000001</></></>
            SOAPElement jobResponse = (SOAPElement) rbody.getChildElements().next();
            SOAPElement jobReturn = (SOAPElement) jobResponse.getChildElements().next();
            long jobId = 0L;

            try {
                jobId = Long.parseLong( jobReturn.getValue() );
            } catch (NumberFormatException e) {
                System.out.println("ERROR PARSING NUMBER ------");
                System.out.println("jobReturn : " + jobReturn + " :::: " + jobReturn.getValue());
            }

            //close SOAP connection
            connection.close();

            //return grendel ID
            return jobId;

        }

    }

    public static String getJobStatus (String jobId) throws Exception {
        MessageFactory factory = MessageFactory.newInstance();
        SOAPMessage message = factory.createMessage();

        SOAPBody body = message.getSOAPBody();
        SOAPFactory soapFactory = SOAPFactory.newInstance();
        Name bodyName = soapFactory.createName("getJobStatus", "", "urn:Grendel");
        SOAPBodyElement bodyElement = body.addBodyElement(bodyName); 
    
        Name name = soapFactory.createName("id");
        SOAPElement xmlStringElem = bodyElement.addChildElement(name);
        xmlStringElem.addTextNode(jobId);

        SOAPConnectionFactory soapConnectionFactory = SOAPConnectionFactory.newInstance();
        SOAPConnection connection = soapConnectionFactory.createConnection();
        
        java.net.URL endpoint = new URL(grendelUrl);

        SOAPMessage response = connection.call(message, endpoint);

        SOAPHeader header = response.getSOAPHeader();
        SOAPBody rbody = response.getSOAPBody();

        //check for a fault
        if ( rbody.hasFault() ) {

            SOAPFault newFault = rbody.getFault();
            Name code = newFault.getFaultCodeAsName();
            String string = newFault.getFaultString();

            connection.close();

            throw new Exception(string);

        } else {

            java.util.Iterator iterator = rbody.getChildElements();
            SOAPElement element = (SOAPElement)iterator.next(); //getJobStatusResponse
            iterator = element.getChildElements();
            SOAPElement wantedElement = (SOAPElement)iterator.next(); //getJobStatusReturn

            connection.close();

            return wantedElement.getValue();

        }
    }

}
