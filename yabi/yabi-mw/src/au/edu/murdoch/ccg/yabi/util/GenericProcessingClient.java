package au.edu.murdoch.ccg.yabi.util;

import java.util.*;
import au.edu.murdoch.ccg.yabi.objects.BaatInstance;
import au.edu.murdoch.ccg.yabi.objects.User;
import org.apache.commons.configuration.*;

public abstract class GenericProcessingClient {

    //variables for concrete methods
    protected String outputDir;
    protected BaatInstance bi;
    
    //instance methods
    public abstract String submitJob () throws Exception;
    public abstract void setInputDirByUsername(String userName);
    public abstract String getJobStatus (String jobId) throws Exception;
    public abstract void fileStageIn ( ArrayList files ) throws Exception;
    public abstract void setStageOutPrefix (String in);
    public abstract void fileStageOut ( ArrayList files ) throws Exception;
    public abstract boolean authenticate ( User user ) throws Exception;
    public abstract boolean isCompleted () throws Exception;
    public abstract boolean hasError () throws Exception;

    //concrete methods
    public void setOutputDir(String location) {
        this.outputDir = location;
    }
    
    public void runAssertions() throws Exception {
        //runs assertions associated with baat file, throws exception if it fails one
    }
}
