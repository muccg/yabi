//
//  GridKillJob.java
//  yabi-mw
//
//  Created by ntt on 20/12/07.
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

import au.edu.murdoch.ccg.yabi.util.GridClient;
import au.edu.murdoch.ccg.yabi.objects.User;
import au.edu.murdoch.ccg.yabi.util.YabiConfiguration;
import org.apache.commons.configuration.*;

public class GridKillJob extends BaseAction {
    
    private Configuration conf;
    private String rootDir;
    
    public GridKillJob () throws ConfigurationException {
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
        String gridepr = request.getParameter("gridepr");
        
        try {
            if (username == null || gridepr == null) {
                throw new Exception("arguments missing");
            }

            GridClient gc = new GridClient();
            gc.authenticate(new User(username));
            
            gc.killJob(gridepr);
            
        } catch (Exception e) {
            e.printStackTrace();
            request.setAttribute("message", "Error killing grid job: "+e.getMessage());
            return mapping.findForward("error");
            
        }
        
        request.setAttribute("message", "successfully killed job");
        
        return mapping.findForward("success");
        
    }
    
}
