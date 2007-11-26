//
//  MailTool.java
//  yabi-mw
//
//  Created by ntt on 30/10/07.
//  Copyright 2007 CCG, Murdoch University. All rights reserved.
//
package au.edu.murdoch.ccg.yabi.util;

import javax.mail.*;
import javax.mail.internet.*;
import java.util.*;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.util.AppDetails;
import java.util.logging.Logger;
import org.apache.commons.configuration.*;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;


/**
* A simple email sender class.
 */
public class MailTool {
    
    private static Logger logger = Logger.getLogger( AppDetails.getAppString() + "." + MailTool.class.getName());
    private String smtpHost;
    private String defaultRcpt;
    private String webappName;
    private String defaultFrom;
    
    public MailTool () {
        try {
            loadConfig();
        } catch (Exception e) {
            logger.severe("failed to load configuration for mail sending");
        }
    }
    
    /**
    * Main method to send a message given on the command line.
     */
    public boolean sendYabiError(String message) {
        try {
            send(smtpHost, defaultRcpt, defaultFrom, webappName+" error", message);
            
            return true;
        } catch (Exception ex) {
            logger.severe("failed to send message. watch for other errors, eh");
            return false;
        }
    }
    
    private void loadConfig() throws ConfigurationException {
        //load config details
        Configuration conf = YabiConfiguration.getConfig();
        smtpHost = conf.getString("smtp.host");
        defaultRcpt = conf.getString("error.mailTo");
        defaultFrom = conf.getString("error.mailFrom");
        webappName = "yabi-"+conf.getString("buildname");
    }
    
    /**
     * "send" method to send the message.
     */
    public static void send(String smtpServer, String to, String from
                            , String subject, String body) throws Exception {
        Properties props = System.getProperties();
        // -- Attaching to default Session, or we could start a new one --
        props.put("mail.smtp.host", smtpServer);
        Session session = Session.getDefaultInstance(props, null);
        // -- Create a new message --
        Message msg = new MimeMessage(session);
        // -- Set the FROM and TO fields --
        msg.setFrom(new InternetAddress(from));
        msg.setRecipients(Message.RecipientType.TO,
                          InternetAddress.parse(to, false));
        // -- We could include CC recipients too --
        // if (cc != null)
        // msg.setRecipients(Message.RecipientType.CC
        // ,InternetAddress.parse(cc, false));
        // -- Set the subject and body text --
        msg.setSubject(subject);
        msg.setText(body);
        // -- Set some other header information --
        msg.setHeader("X-Mailer", "JavaMail");
        msg.setSentDate(new Date());
        // -- Send the message --
        Transport.send(msg);
        logger.info("Email error message dispatched to "+to);
    }

    public static String trapStackTrace(Exception e) {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        PrintStream ps = new PrintStream(baos);
        e.printStackTrace(ps);
        return baos.toString();
    }
}