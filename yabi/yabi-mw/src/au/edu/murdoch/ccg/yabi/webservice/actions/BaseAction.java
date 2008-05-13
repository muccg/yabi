package au.edu.murdoch.ccg.yabi.webservice.actions;

import org.jbpm.graph.def.*;
import org.jbpm.graph.exe.*;
import org.jbpm.*;
import java.util.*;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

public abstract class BaseAction extends Action {

    //shared variables amongst all actions
    protected JbpmConfiguration jbpmConfiguration = JbpmConfiguration.getInstance("yabi-jbpm.cfg.xml");
    protected static final String TYPE_XML = "xml";
    protected static final String TYPE_TXT = "text";
    protected static final String TYPE_JSON = "json";

    //convenience methods for all actions

}
