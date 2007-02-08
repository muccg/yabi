package au.edu.murdoch.ccg.yabi.util;

import java.util.*;
import au.edu.murdoch.ccg.yabi.objects.User;

public abstract class GenericProcessingClient {

    //instance methods
    public abstract long submitJob () throws Exception;
    public abstract void setOutputDir(String dir);
    public abstract String getJobStatus (String jobId) throws Exception;
    public abstract void fileStageIn ( ArrayList files ) throws Exception;
    public abstract void setStageOutPrefix (String in);
    public abstract void fileStageOut ( ArrayList files ) throws Exception;
    public abstract boolean authenticate ( User user ) throws Exception;
    public abstract boolean isCompleted () throws Exception;
    public abstract boolean hasError () throws Exception;

}
