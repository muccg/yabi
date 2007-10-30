package au.edu.murdoch.ccg.yabi.util;

import java.io.*;
import java.util.*;
import javax.xml.parsers.*;
import org.w3c.dom.*;

import java.util.logging.Logger;

public class ToolMan {

    private static List tools;
    private static final String toolFileLocation = "/usr/local/share/grendel/xml/tools/tools.xml";
    private static Document sourceDOM;
    private static Logger logger = Logger.getLogger( AppDetails.getAppString() + "." + ToolMan.class.getName());

    public ToolMan () {}

    public List loadTools() {
        if (tools == null) {
            try {
                DocumentBuilder db =  DocumentBuilderFactory.newInstance().newDocumentBuilder();
                sourceDOM = db.parse( toolFileLocation );

                NodeList toolNodes = sourceDOM.getElementsByTagName("tool");

                tools = new ArrayList();
                for (int i = 0; i < toolNodes.getLength(); i++) {
                    tools.add( toolNodes.item(i).getAttributes().getNamedItem("name").getNodeValue() );
                }

            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        return tools;
    }

    public static void main(String[] args) {
        ToolMan tm = new ToolMan();
        List tools = tm.loadTools();

        logger.info(tools.toString());
    }

}
