package au.edu.murdoch.ccg.yabi.util;

import java.io.*;

public class SymLink {

    public static void createSymLink( String from, String to ) throws Exception {
        //TODO make this safe from hacking. Filenames should not have illegal characters
        Runtime.getRuntime().exec("ln -s "+from+" "+to);
    }

    public static void deleteSymLink( String location ) {
        File link = new File(location);
        link.delete();
    }

}
