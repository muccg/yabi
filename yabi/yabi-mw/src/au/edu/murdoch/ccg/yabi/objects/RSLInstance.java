package au.edu.murdoch.ccg.yabi.objects;

public class RSLInstance extends BaatInstance {

    public RSLInstance (String toolName) throws Exception {
        super(toolName);
    }

    //extending the BaatInstance class gives us the Baat 'validation' and all we need to do is re-implement the exportXML() method
    public String exportXML() {
        //TODO either use JAXP to do an XSLT transform of the Baat
        //TODO or simply grab the relevant values and insert into a template RSL Document
        return "";
    }

}
