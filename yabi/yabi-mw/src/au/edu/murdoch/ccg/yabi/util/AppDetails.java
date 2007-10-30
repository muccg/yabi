package au.edu.murdoch.ccg.yabi.util;

public class AppDetails {
    
    private static String appName = "yabi-mw";
    
    public static String getAppString() {
        return appName;
    }
    
    public static String getAppString( String newAppName ) {
        appName = newAppName;
        return getAppString();
    }
}