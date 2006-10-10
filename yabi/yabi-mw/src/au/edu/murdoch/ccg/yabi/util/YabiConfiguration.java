package au.edu.murdoch.ccg.yabi.util;

import org.apache.commons.configuration.*;

public class YabiConfiguration {

    private static Configuration yconf = null;   //singleton

    //could synchronize this but not really fussed if we load the config twice
    public static Configuration getConfig() throws ConfigurationException {
        if (yconf == null) {
            yconf = new PropertiesConfiguration("yabi.properties");
        }
        return yconf;
    }
}
