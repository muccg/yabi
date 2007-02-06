<html>
<body>
<form action="../../dispatchXML.ws" method="POST">
<textarea name="jobXML" cols="40" rows="20">
&lt;?xml version="1.0"?&gt;
&lt;yabi-job&gt;
  &lt;variables&gt;
    &lt;variable key="unit_0-m" value="clone_0-m"/&gt;
    &lt;variable key="unit_0-q" value="clone_0-q"/&gt;
    &lt;variable key="unit_1--oneline" value="clone_1--oneline"/&gt;
  &lt;/variables&gt;
  &lt;process-definition&gt;
    &lt;start-state name="start"&gt;
      &lt;transition to="unit_0"/&gt;
    &lt;/start-state&gt;
    &lt;node name="unit_0"&gt;
      &lt;action class="au.edu.murdoch.ccg.yabi.actions.SubmitJobAction"/&gt;
      &lt;transition to="unit_0-check" name="next"/&gt;
      &lt;transition to="error" name="error"/&gt;
    &lt;/node&gt;
    &lt;node name="unit_0-check"&gt;
      &lt;action class="au.edu.murdoch.ccg.yabi.actions.WaitForJobAction"/&gt;
      &lt;transition to="unit_1" name="next"/&gt;
      &lt;transition to="error" name="error"/&gt;
    &lt;/node&gt;
    &lt;node name="unit_1"&gt;
      &lt;action class="au.edu.murdoch.ccg.yabi.actions.SubmitJobAction"/&gt;
      &lt;transition to="unit_1-check" name="next"/&gt;
      &lt;transition to="error" name="error"/&gt;
    &lt;/node&gt;
    &lt;node name="unit_1-check"&gt;
      &lt;action class="au.edu.murdoch.ccg.yabi.actions.WaitForJobAction"/&gt;
      &lt;transition to="end" name="next"/&gt;
      &lt;transition to="error" name="error"/&gt;
    &lt;/node&gt;
    &lt;end-state name="end"/&gt;
  &lt;/process-definition&gt;
  &lt;jobName&gt;testjob&lt;/jobName&gt;
  &lt;userName&gt;ntakayama&lt;/userName&gt;
  &lt;year&gt;2007&lt;/year&gt;
  &lt;month&gt;02&lt;/month&gt;
&lt;/yabi-job&gt;
</textarea>
<input type="submit">
</form>
</body>
</html>
