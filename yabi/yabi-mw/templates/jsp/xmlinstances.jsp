<?xml version="1.0" encoding="ISO-8859-1"?>
<%@ page import="org.jbpm.graph.def.*, org.jbpm.graph.exe.*, org.jbpm.*, java.util.*" %>
<%@ page contentType="text/xml" %>
<xml-response type="data">
<%
  JbpmConfiguration jbpmConfiguration = JbpmConfiguration.getInstance("@jbpmconfigfile@");
  

  JbpmContext jbpm = jbpmConfiguration.createJbpmContext();
  
  try {
  	long procDefId = Long.parseLong(request.getParameter("id"));
  	
  	ProcessDefinition pd = jbpm.getGraphSession().getProcessDefinition( procDefId );
%>
    <process-definition name="<%= pd.getName() %>" version="<%= pd.getVersion() %>">
<%
	List instances = jbpm.getGraphSession().findProcessInstances( procDefId ); 
  	Iterator iter = instances.iterator();
  	while (iter.hasNext()) {
  		ProcessInstance pi = (ProcessInstance) iter.next();
%>
    <instance>
        <hasEnded><%= (pi.hasEnded()) %></hasEnded>
        <id><%= pi.getId() %></id>
        <start><%= pi.getStart() %></start>
        <end><%= pi.getEnd() %></end>
        <tokens>
<%      Iterator titer = pi.findAllTokens().iterator();
        while (titer.hasNext()) {
            Token currentToken = (Token) titer.next();
%>
            <token name="<%= currentToken.getName() %>" node="<%= currentToken.getNode().getFullyQualifiedName() %>"/>
<%
    }
%>
        </tokens>
        <contextVariables>
<%
		Iterator viter = pi.getContextInstance().getVariables().keySet().iterator();
		while (viter.hasNext()) {
			String keyName = (String) viter.next();
%>
            <variable key="<%= keyName %>" value="<%= pi.getContextInstance().getVariable(keyName) %>"/>
<%
		}
%>
        </contextVariables>
    </instance>
<%
	}
%>
    </process-definition>
<%
  } catch (Exception e) {
  } finally {
    jbpm.close();
  }
%>
</xml-response>
