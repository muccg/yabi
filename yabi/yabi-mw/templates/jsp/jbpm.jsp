<%@ page import="org.jbpm.graph.def.*, org.jbpm.graph.exe.*, org.jbpm.*, java.util.*" %>
<%
  JbpmConfiguration jbpmConfiguration = JbpmConfiguration.getInstance("@jbpmconfigfile@");
  

  JbpmContext jbpm = jbpmConfiguration.createJbpmContext();
  
  long procId;
  
  try {
  	ProcessDefinition processDefinition = jbpm.getGraphSession().findLatestProcessDefinition("submitGrendel");
  
    ProcessInstance processInstance = 
      new ProcessInstance(processDefinition);

    processInstance.getContextInstance().setVariable("checkGrendel.input.jobId", "derived(submitGrendel.output.jobId)");
    processInstance.getContextInstance().setVariable("submitGrendel.input.jobXML", "<?xml version='1.0'?> <!DOCTYPE baat SYSTEM 'http://cbbc.murdoch.edu.au/dtd/baat.dtd'> <baat> <job toolPath='/usr/local/bin/blastall' toolName='blast'> <inputFile>data.zip</inputFile> <outputFile>1234567890.zip</outputFile> <parameterList> <parameter name='dataset' mandatory='Yes' switchOnly='No' switch='-d' value='nr' rank='1'/> <parameter name='dataset' mandatory='Yes' switchOnly='No' switch='-p' value='blastx' rank='2'/> <parameter name='dataset' mandatory='Yes' switchOnly='No' switch='-i' value='data.txt' rank='3'/> <parameter name='dataset' mandatory='Yes' switchOnly='No' switch='-d' value='nr' rank='4'/> <parameter name='dataset' mandatory='Yes' switchOnly='No' switch='-d' value='nr' rank='5'/> <parameter name='dataset' mandatory='Yes' switchOnly='No' switch='-d' value='nr' rank='6'/> </parameterList> <grendel id='1234567'> <option> <name>eric</name> </option> <option> <name>cache</name> </option> <option> <name>label</name> <value>igrow</value> </option> </grendel> <priority>-20</priority> <executionHost>cbbc-n09</executionHost> <batchNumber>1234567890</batchNumber> <status>C</status> <startTime>13 oct 2003 12:00:01</startTime> <stopTime>13 oct 2003 12:00:02</stopTime> <submittedTime>13 oct 2003 12:00:00</submittedTime> <submitUser>some user</submitUser> <submitLabel>some_random_label</submitLabel> </job> </baat> ");
    processInstance.getContextInstance().setVariable("submitGrendel.input.attachment", "file:///export/home/tech/ntakayama/devel/ccg/yabi-mw/testdata/DQ6060.zip");
      
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
