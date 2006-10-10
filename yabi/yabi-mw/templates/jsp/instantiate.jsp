<html>
<body>
<form action="../../instantiate.ws" method="POST">
process def id: <input type="text" name="id"><br/>
submitGrendel.input.jobType: <input type="text" name="submitGrendel.input.jobType" value="grendel"><br/>
submitGrendel.input.toolName: <input type="text" name="submitGrendel.input.toolName" value="blast"><br/>
submitGrendel.input.-d: <input type="text" name="submitGrendel.input.-d" value="nr"><br/>
submitGrendel.input.-p: <input type="text" name="submitGrendel.input.-p" value="blastx"><br/>
submitGrendel.input.-i: <input type="text" name="submitGrendel.input.-i" value="data.txt"><br/>
submitGrendel.input.-o: <input type="text" name="submitGrendel.input.-o" value="output.txt"><br/>
checkGrendel.input.jobId <input type="text" name="checkGrendel.input.jobId" value="derived(submitGrendel.output.jobId)"><br/>
<input type="submit">
</form>
</body>
</html>
