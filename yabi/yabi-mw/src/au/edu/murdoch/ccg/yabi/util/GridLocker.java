package au.edu.murdoch.ccg.yabi.util;

import java.util.concurrent.*;

/**
 * GridLocker
 * implements a singleton that allows a limited-size queue for gridftp, submission and status checks
 */

public class GridLocker {

    private static int maxFileTransfers = 5;
    private static int maxSubmissions = 5;
    private static int maxStatusChecks = 50;

    //the queues
    private BlockingQueue<GridClient> transferQueue = new LinkedBlockingQueue<GridClient>(maxFileTransfers);

    //singleton
    private static GridLocker gl = null;

    //use a basic locking mechanism that is not performance driven
    public synchronized static GridLocker getInstance() {
        if(gl == null) {
            gl = new GridLocker();
        }
        return gl;
    }

    public void waitForTransferSlot(GridClient gc) {
        try {
            transferQueue.put(gc);
        } catch (InterruptedException ie) {}
    }

    public void releaseTransferSlot(GridClient gc) {
        transferQueue.remove(gc);
    }

    public int getTransientRemainingTransferCount() {
        return transferQueue.remainingCapacity();
    }

}
