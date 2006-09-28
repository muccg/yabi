package au.edu.murdoch.ccg.yabi.util;

import org.apache.axis.soap.*;
import javax.xml.soap.*;
import java.util.*;
import java.net.*;
import java.io.*;

public class SoapTestCheck {

    public static String grendelUrl = "http://grendel.localdomain:8080/axis-1_2_1/services/grendel";

    public static void main (String[] args) {
        try {
            MessageFactory factory = MessageFactory.newInstance();
            SOAPMessage message = factory.createMessage();

            SOAPBody body = message.getSOAPBody();
            SOAPFactory soapFactory = SOAPFactory.newInstance();
            Name bodyName = soapFactory.createName("getJobStatus", "", "urn:Grendel");
            SOAPBodyElement bodyElement = body.addBodyElement(bodyName); 
    
            Name name = soapFactory.createName("id");
            SOAPElement xmlStringElem = bodyElement.addChildElement(name);
            xmlStringElem.addTextNode(args[0]);

            SOAPConnectionFactory soapConnectionFactory = SOAPConnectionFactory.newInstance();
            SOAPConnection connection = soapConnectionFactory.createConnection();
        
            java.net.URL endpoint = new URL(grendelUrl);

            SOAPMessage response = connection.call(message, endpoint);

            SOAPHeader header = response.getSOAPHeader();
            SOAPBody rbody = response.getSOAPBody();

            java.util.Iterator iterator = rbody.getChildElements();
            SOAPElement element = (SOAPElement)iterator.next(); //getJobStatusResponse
            iterator = element.getChildElements();
            SOAPElement wantedElement = (SOAPElement)iterator.next(); //getJobStatusReturn

            System.out.println("Response : " + wantedElement.getValue());

            connection.close();
        } catch (Exception e) {
            System.out.println(e.getClass() + " : " + e.getMessage());
            e.printStackTrace();
        }

    }

}
