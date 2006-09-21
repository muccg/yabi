<html>
<body>
<h3>JBPM test</h3>

<ul>
	<li><a href="jbpmdeploy.jsp">deploy a test process named 'delay'</a>
	<li><a href="jbpm.jsp">start an instance of 'delay' (will pause for 20 seconds)</a>
	<li>
	<li><a href="jbpmforkdeploy.jsp">deploy a test process named 'forkdelay'</a>
	<li><a href="jbpmfork.jsp">start an instance of 'forkdelay' (will fork and then pause for 20 seconds)</a>
	<li>
	<li><a href="jbpmdefs.jsp">view all deployed process definitions (and completed instances)</a>
</ul>

<h4>XML web services</h4>

<ul>
    <li><a href="../definitions.ws">list all deployed definitions</a>
    <li>show details for instances of a definition... <form action="../instances.ws">definition id: <input name="id"><input type="submit"></form>
</ul>

</body>
</html>
