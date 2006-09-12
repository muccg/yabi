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
      "  <state name='delay1'>" +
      "    <timer duedate='15 seconds'>" +
      "      <action class='au.edu.murdoch.ccg.yabi.actions.JBPMDelay' />" +
      "    </timer>" +
      "    <transition name='next' to='join'/>" +
      "  </state>" +
      "  <state name='delay2'>" +
      "    <timer duedate='2 minutes'>" +
      "      <action class='au.edu.murdoch.ccg.yabi.actions.JBPMDelay' />" +
      "    </timer>" +
      "    <transition to='join' name='next' />" +
      "  </state>" +
      "  <join name='join'>" +
      "    <transition to='delay3' />" +
      "  </join>" +
      "  <state name='delay3'>" +
      "    <timer duedate='2 minutes'>" +
      "      <action class='au.edu.murdoch.ccg.yabi.actions.JBPMDelay' />" +
      "    </timer>" +
      "    <transition to='end' name='next' />" +
      "  </state>" +
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
