<%@ page import="org.jbpm.graph.def.*, org.jbpm.graph.exe.*, org.jbpm.*" %>
<%
  JbpmConfiguration jbpmConfiguration = JbpmConfiguration.getInstance("@jbpmconfigfile@");
  

  JbpmContext jbpm = jbpmConfiguration.createJbpmContext();
  
  try {
  	
    ProcessDefinition processDefinition = ProcessDefinition.parseXmlString(
      "<process-definition name='submitGrendel'>" +
      "  <start-state name='start'>" +
      "    <transition to='submitGrendel' />" +
      "  </start-state>" +
      "  <node name='submitGrendel'>" +
      "    <action class='au.edu.murdoch.ccg.yabi.actions.SubmitGrendelXMLJobAction' />" +
      "    <transition to='checkGrendel' name='next' />" +
      "    <transition to='error' name='error' />" +
      "  </node>" +
      "  <node name='checkGrendel'>" +
      "    <action class='au.edu.murdoch.ccg.yabi.actions.GrendelJobStatusAction' />" +
      "    <transition to='end' name='next'/>" +
      "    <transition to='error' name='error'/>" +
      "  </node>" +
      "  <end-state name='end' />" +
      "  <end-state name='error' />" +
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
