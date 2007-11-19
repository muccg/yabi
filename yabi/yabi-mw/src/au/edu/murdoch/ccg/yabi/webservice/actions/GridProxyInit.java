//
//  GridProxyInit.java
//  yabi-mw
//
//  Created by ntt on 1/11/07.
//  Copyright 2007 CCG, Murdoch University. All rights reserved.
//
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

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import au.edu.murdoch.ccg.yabi.util.cog.YabiGridProxyInit;
import org.apache.commons.configuration.*;

public class GridProxyInit extends BaseAction {
    
    private String rootDir = "";
    Configuration conf = null;
        
    public GridProxyInit () throws ConfigurationException {
        super();
        loadConfig();
    }
    
    private void loadConfig() throws ConfigurationException {
        //load config details
        this.conf = YabiConfiguration.getConfig();
        this.rootDir = conf.getString("yabi.rootDirectory");
    }
    
    public ActionForward execute(ActionMapping mapping, ActionForm form, HttpServletRequest request, HttpServletResponse response) throws Exception {
                                     
         try {
             
             //create proxy file
             String certFile = this.rootDir + request.getParameter("username")+"/certificates/usercert.pem";
             String userKey = this.rootDir +request.getParameter("username")+"/certificates/userkey.pem";
             String proxyFile = this.rootDir +request.getParameter("username")+"/certificates/ivec_proxy.pem";
             YabiGridProxyInit ygpi = new YabiGridProxyInit();
             ygpi.initProxy(certFile, userKey, request.getParameter("password"), proxyFile);
             
         } catch (Exception e) {
             
             request.setAttribute("message", "Failed authentication: "+e.getClass().getName()+" : "+e.getMessage() + "\n\n" + trapStackTrace(e));
             return mapping.findForward("error");
             
         }
         
         request.setAttribute("message", "success");
         
         return mapping.findForward("success");
         
     }
    
    public static String trapStackTrace(Exception e) {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        PrintStream ps = new PrintStream(baos);
        e.printStackTrace(ps);
        return baos.toString();
    }
     
}
