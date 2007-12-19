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
        
        String certFile = "";
        String userKey = "";
        String username = request.getParameter("username");
        String password = request.getParameter("password");
        String expirySeconds = request.getParameter("expiry");
        int expiry = 0;
        YabiGridProxyInit ygpi;
        
        try {
            if (password == null) {
                throw new Exception("Password missing");
            }
            
            //create proxy file
            certFile = this.rootDir + username +"/certificates/usercert.pem";
            userKey = this.rootDir + username +"/certificates/userkey.pem";
            String proxyFile = this.rootDir + username +"/certificates/ivec_proxy.pem";
            if (expirySeconds == null || expirySeconds.length() < 1) {
                ygpi = new YabiGridProxyInit();
            } else {
                expiry = Integer.parseInt(expirySeconds);
                ygpi = new YabiGridProxyInit(expiry);
            }
            ygpi.initProxy(certFile, userKey, password, proxyFile);
            
        } catch (Exception e) {
            
            request.setAttribute("message", "Failed authentication for "+request.getParameter("username")+" using certFile: "+certFile+" userKey: "+userKey+" error: "+e.getClass().getName()+" : "+e.getMessage() + "\n\n" + trapStackTrace(e));
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
