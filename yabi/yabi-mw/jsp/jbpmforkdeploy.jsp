<%@ page import="org.jbpm.graph.def.*, org.jbpm.graph.exe.*, org.jbpm.*" %>
<%
  JbpmConfiguration jbpmConfiguration = JbpmConfiguration.getInstance();
  

  JbpmContext jbpm = jbpmConfiguration.createJbpmContext();
  
  try {
  	
    ProcessDefinition processDefinition = ProcessDefinition.parseXmlString(
      "<process-definition name='forkdelay'>" +
      "  <start-state name='start'>" +
      "    <transition to='fork' />" +
      "  </start-state>" +
      "  <fork name='fork'>" +
      "    <transition name='left' to='delay1' />" +
      "    <transition name='right' to='delay2' />" +
      "  </fork>" +
      "  <node name='delay1'>" +
      "    <action class='au.edu.murdoch.ccg.yabi.actions.JBPMDelay' />" +
      "    <transition to='join' name='next' />" +
      "  </node>" +
      "  <node name='delay2'>" +
      "    <action class='au.edu.murdoch.ccg.yabi.actions.JBPMDelay' />" +
      "    <transition to='join' name='next' />" +
      "  </node>" +
      "  <join name='join'>" +
      "    <transition to='end' />" +
      "  </join>" +
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