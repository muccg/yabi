package au.edu.murdoch.ccg.yabi.objects;

public class OutputFileAssertion {
    public String extension = "";
    public boolean mustExist = false;
    public boolean mustContainData = false;
    public String mustContainString = null;
    public String mustNotContainString = null;
    public boolean mustNotExist = false;
}