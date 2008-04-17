package au.edu.murdoch.ccg.yabi.util;

import java.io.*;

import java.util.logging.Logger;

public class SymLink {

    private static Logger logger = Logger.getLogger( AppDetails.getAppString() + "." + SymLink.class.getName());

    public static void createSymLink( String from, String to ) throws Exception {
        //TODO make this safe from hacking. Filenames should not have illegal characters

        String[] command = {"ln","-s",from,to};

        Runtime.getRuntime().exec(command);
        logger.info("ln -s '"+from+"' '"+to+"'");
    }

    public static void deleteSymLink( String location ) {
        File link = new File(location);
        link.delete();
    }

}
