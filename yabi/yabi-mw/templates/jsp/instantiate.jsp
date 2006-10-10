<html>
<body>
<form action="../../instantiate.ws" method="POST">
process def id: <input type="text" name="id"><br/>
submit.input.jobType: <input type="text" name="submit.input.jobType" value="grendel"><br/>
submit.input.toolName: <input type="text" name="submit.input.toolName" value="blast"><br/>
submit.input.-d: <input type="text" name="submit.input.-d" value="nr"><br/>
submit.input.-p: <input type="text" name="submit.input.-p" value="blastx"><br/>
submit.input.-i: <input type="text" name="submit.input.-i" value="data.txt"><br/>
submit.input.-o: <input type="text" name="submit.input.-o" value="output.txt"><br/>
check.input.jobType: <input type="text" name="check.input.jobType" value="grendel"><br/>
check.input.jobId <input type="text" name="check.input.jobId" value="derived(submit.output.jobId)"><br/>
<input type="submit">
</form>
</body>
</html>
