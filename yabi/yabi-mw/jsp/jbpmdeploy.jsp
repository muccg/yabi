<%@ page import="org.jbpm.graph.def.*, org.jbpm.graph.exe.*, org.jbpm.*" %>
<%
  JbpmConfiguration jbpmConfiguration = JbpmConfiguration.getInstance();
  

  JbpmContext jbpm = jbpmConfiguration.createJbpmContext();
  
  try {
  	
    ProcessDefinition processDefinition = ProcessDefinition.parseXmlString(
      "<process-definition name='delay'>" +
      "  <start-state name='start'>" +
      "    <transition to='delay' />" +
      "  </start-state>" +
      "  <node name='delay'>" +
      "    <action class='au.edu.murdoch.ccg.yabi.actions.JBPMDelay' />" +
      "    <transition to='end' name='next' />" +
      "  </node>" +
      "  <end-state name='end' />" +
      "</process-definition>"
    ); 
  
    jbpm.getGraphSession().deployProcessDefinition(processDefinition);
  
  } catch (Exception e) {
%>
<%= e.getMessage() %>
<%
  } finally {
    jbpm.close();
  }
%>
Process definition saved.