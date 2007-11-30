//
//  GridProxyExpiration.java
//  yabi-mw
//
//  Created by ntt on 1/11/07.
//  Copyright 2007 CCG, Murdoch University. All rights reserved.
//
package au.edu.murdoch.ccg.yabi.webservice.actions;

import java.util.*;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;

import au.edu.murdoch.ccg.yabi.util.cog.YabiGridProxyModel;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import org.apache.commons.configuration.*;

public class GridProxyExpiration extends BaseAction {
    
    private Configuration conf;
    private String rootDir;
    
    public GridProxyExpiration () {
        super();
        loadConfig();
    }
    
    private void loadConfig() throws ConfigurationException {
        //load config details
        this.conf = YabiConfiguration.getConfig();
        this.rootDir = conf.getString("yabi.rootDirectory");
    }
    
    public ActionForward execute(ActionMapping mapping, ActionForm form, HttpServletRequest request, HttpServletResponse response) throws Exception {
        
        String username = request.getParameter("username");
        String gridname = request.getParameter("grid");
        long secondsLeft = 0;
        
        try {
            if (username == null || gridname == null) {
                throw new Exception("arguments missing");
            }
            
            YabiGridProxyModel ygpm = new YabiGridProxyModel();
            secondsLeft = ygpm.getTimeLeft(this.rootDir + username +"/certificates/"+ gridname +"_proxy.pem");
            
        } catch (Exception e) {
            
            request.setAttribute("message", "Proxy expired or unavailable");
            return mapping.findForward("error");
            
        }
        
        request.setAttribute("message", ""+secondsLeft);
        
        return mapping.findForward("success");
        
    }
    
}
