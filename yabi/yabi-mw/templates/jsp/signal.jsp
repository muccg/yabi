<%@ page import="org.jbpm.graph.def.*, org.jbpm.graph.exe.*, org.jbpm.*, java.util.*" %>
<%
  JbpmConfiguration jbpmConfiguration = JbpmConfiguration.getInstance("yabi-jbpm.cfg.xml");
  

  JbpmContext jbpm = jbpmConfiguration.createJbpmContext();
  
  try {
  	long procId = Long.parseLong(request.getParameter("id"));
  	
  	ProcessInstance pi = jbpm.getGraphSession().getProcessInstance( procId );

    pi.signal();

  } catch (Exception e) {
%>
<%= e.getMessage() %>
<%
  } finally {
    jbpm.close();
  }
%>
