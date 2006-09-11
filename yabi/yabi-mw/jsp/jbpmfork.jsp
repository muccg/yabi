<%@ page import="org.jbpm.graph.def.*, org.jbpm.graph.exe.*, org.jbpm.*, java.util.*" %>
<%
  JbpmConfiguration jbpmConfiguration = JbpmConfiguration.getInstance();
  

  JbpmContext jbpm = jbpmConfiguration.createJbpmContext();
  
  long procId;
  
  try {
  
  	ProcessDefinition processDefinition = jbpm.getGraphSession().findLatestProcessDefinition("forkdelay");
  
    ProcessInstance processInstance = 
      new ProcessInstance(processDefinition);
      
    processInstance.getContextInstance().setVariable("input param 1", "recognize");
%>
<%= processInstance.getId() %>
<%  
	//do a transactional close and reopen to save the start 
	jbpm.save(processInstance);
	procId = processInstance.getId();
	jbpm.close();
	jbpm = jbpmConfiguration.createJbpmContext();
	
	//resume processing now that we've saved
	processInstance = jbpm.loadProcessInstanceForUpdate(procId);
	Token token = processInstance.getRootToken();
%>
<%= token.getNode() %>
<%
	token.signal();
%>
<%= token.getNode() %>
<br>
should be at end<br>
<%	Iterator iter = processInstance.getContextInstance().getVariables().keySet().iterator();
	while (iter.hasNext()) {
		String keyName = (String) iter.next();
%>
<%= keyName %> : <%= processInstance.getContextInstance().getVariable(keyName) %><br/>
<%
	}
	
	//an explicit save() is unnecessary now that we have the process open for update
    //jbpm.save(processInstance);
  } catch (Exception e) {
%>
<%= e.getMessage() %>
<%
  } finally {
    jbpm.close();
  }
%>