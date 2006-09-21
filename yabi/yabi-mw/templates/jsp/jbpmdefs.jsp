<%@ page import="org.jbpm.graph.def.*, org.jbpm.graph.exe.*, org.jbpm.*, java.util.*" %>
<h3>Deployed process definitions</h3>
<%
  JbpmConfiguration jbpmConfiguration = JbpmConfiguration.getInstance("@jbpmconfigfile@");
  

  JbpmContext jbpm = jbpmConfiguration.createJbpmContext();
  
  try {
  	
  	List processDefs = jbpm.getGraphSession().findLatestProcessDefinitions();
  	Iterator iter = processDefs.iterator();
  	while (iter.hasNext()) {
  		ProcessDefinition pd = (ProcessDefinition) iter.next();
%>
<%= pd.getName() %>  (v <%= pd.getVersion() %>)   
	<a href="jbpminstances.jsp?id=<%= pd.getId() %>">(view instances)</a><br/>
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
