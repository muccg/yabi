<?xml version="1.0" encoding="ISO-8859-1"?>
<%@ page import="org.jbpm.graph.def.*, org.jbpm.graph.exe.*, org.jbpm.*, java.util.*" %>
<%@ page contentType="text/xml" %>
<xml-response type="data">
<%
  JbpmConfiguration jbpmConfiguration = JbpmConfiguration.getInstance("@jbpmconfigfile@");
  

  JbpmContext jbpm = jbpmConfiguration.createJbpmContext();
  
  try {
  	
  	List processDefs = jbpm.getGraphSession().findLatestProcessDefinitions();
  	Iterator iter = processDefs.iterator();
  	while (iter.hasNext()) {
  		ProcessDefinition pd = (ProcessDefinition) iter.next();
%>
  <process-definition>
    <name><%= pd.getName() %></name>
    <version><%= pd.getVersion() %></version>
    <id><%= pd.getId() %></id>
  </process-definition>
<%
	}
  } catch (Exception e) {
  } finally {
    jbpm.close();
  }
%>
</xml-response>
