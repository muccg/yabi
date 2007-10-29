package au.edu.murdoch.ccg.yabi.util;

import java.io.*;

import java.util.logging.Logger;

public class SymLink {

    private static Logger logger = Logger.getLogger(SymLink.class.getName());

    public static void createSymLink( String from, String to ) throws Exception {
        //TODO make this safe from hacking. Filenames should not have illegal characters

        Runtime.getRuntime().exec("ln -s "+from+" "+to);
        logger.info("ln -s "+from+" "+to);
    }

    public static void deleteSymLink( String location ) {
        File link = new File(location);
        link.delete();
    }

}
