package au.edu.murdoch.ccg.yabi.util;

import java.util.*;
import java.io.*;
import au.edu.murdoch.ccg.yabi.objects.BaatInstance;
import au.edu.murdoch.ccg.yabi.objects.User;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import org.apache.commons.configuration.*;

public class NullClient extends GenericProcessingClient {

    //constructors
    public NullClient( BaatInstance bi ) throws ConfigurationException {
    }

    //setter
    public void setOutputDir(String location) {
    }

    public void setInputDirByUsername(String userName) {
    }

    //instance methods
    public long submitJob () throws Exception {
        return 0L;
    }

    public String getJobStatus (String jobId) throws Exception {
        return "C";
    }

    public void fileStageIn ( ArrayList files ) throws Exception {
    }

    //define a prefix to prepend to all staged out filenames to allow different tasks to not conflict
    public void setStageOutPrefix ( String prefix ) {
    }

    public void fileStageOut ( ArrayList files ) throws Exception {
    }

    public boolean authenticate ( User user ) throws Exception {
        return true;
    }

    public boolean isCompleted () throws Exception {
        return true;
    }

    public boolean hasError () throws Exception {
        return false;
    }   

}
