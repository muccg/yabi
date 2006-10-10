<html>
<body>
<form action="../../deploy.ws" method="POST">
<textarea name="definition" cols="40" rows="20">
&lt;process-definition name='submit'&gt;
  &lt;start-state name='start'&gt;
    &lt;transition to='submit' /&gt;
  &lt;/start-state&gt;
  &lt;node name='submit'&gt;
    &lt;action class='au.edu.murdoch.ccg.yabi.actions.SubmitJobAction' /&gt;
    &lt;transition to='check' name='next' /&gt;
    &lt;transition to='error' name='error' /&gt;
  &lt;/node&gt;
  &lt;node name='check'&gt;
    &lt;action class='au.edu.murdoch.ccg.yabi.actions.WaitForJobAction' /&gt;
    &lt;transition to='end' name='next'/&gt;
    &lt;transition to='error' name='error'/&gt;
  &lt;/node&gt;
  &lt;end-state name='end' /&gt;
  &lt;end-state name='error' /&gt;
&lt;/process-definition&gt;
</textarea>
<input type="submit">
</form>
</body>
</html>
