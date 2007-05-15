package au.edu.murdoch.ccg.yabi.util;

import au.edu.murdoch.ccg.yabi.objects.*;

public class ProcessingClientFactory {

    public static GenericProcessingClient createProcessingClient(String type, BaatInstance bi) throws Exception {
        if (type != null) {
            if (type.compareTo("grendel") == 0) {
                return new GrendelClient(bi);
            }
            if (type.compareTo("gt4") == 0) {
            }
            if (type.compareTo("local") == 0) {
                return new LocalClient(bi);
            }
            if (type.compareTo("none") == 0) {
                return new NullClient(bi);
            }
        }
        //if we fall through to here we have a problem
        throw new Exception("No such processing client type found: "+type);
    }

}
