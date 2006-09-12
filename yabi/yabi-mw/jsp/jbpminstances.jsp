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
<div style="background-color:#eee;">current node: <%= pi.getRootToken().getNode().getFullyQualifiedName() %></div>
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
