<%@ page import="org.jbpm.graph.def.*, org.jbpm.graph.exe.*, org.jbpm.*, java.util.*" %>
<h3>Process instances</h3>
<%
  JbpmConfiguration jbpmConfiguration = JbpmConfiguration.getInstance();
  

  JbpmContext jbpm = jbpmConfiguration.createJbpmContext();
  
  try {
  	long procDefId = Long.parseLong(request.getParameter("id"));
  	
  	ProcessDefinition pd = jbpm.getGraphSession().getProcessDefinition( procDefId );
%>
<h4>Process Definition: <%= pd.getName() %> (v <%= pd.getVersion() %>)</h4>
<%
	List instances = jbpm.getGraphSession().findProcessInstances( procDefId ); 
  	Iterator iter = instances.iterator();
  	while (iter.hasNext()) {
  		ProcessInstance pi = (ProcessInstance) iter.next();
%>
<div style="background-color:<%= (pi.hasEnded())?"#eee":"#cec" %>;"><%= pi.getId() %> : start=<%= pi.getStart() %>  end=<%= pi.getEnd() %></div>
<b>Tokens</b> : <%  Iterator titer = pi.findAllTokens().iterator();
    while (titer.hasNext()) {
        Token currentToken = (Token) titer.next();
%>
    <%= currentToken.getName() %> (@node= <%= currentToken.getNode().getFullyQualifiedName() %>)<br/>
<%
    }
%>
<div style="margin-left:80px;font-size:0.9em;">
<%
		Iterator viter = pi.getContextInstance().getVariables().keySet().iterator();
		while (viter.hasNext()) {
			String keyName = (String) viter.next();
%>
<%= keyName %> : <%= pi.getContextInstance().getVariable(keyName) %><br/>
<%
		}
%>
</div>
<%
	}
  } catch (Exception e) {
%>
<%= e.getMessage() %>
<%
  } finally {
    jbpm.close();
  }
%>
