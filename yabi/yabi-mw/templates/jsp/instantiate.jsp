<html>
<body>
<form action="../../instantiate.ws" method="POST">
process def id: <input type="text" name="id"><br/>
submitGrendel.input.jobXML: 
<textarea name="submitGrendel.input.jobXML" cols="40" rows="40">
&lt;?xml version='1.0'?&gt; &lt;!DOCTYPE baat SYSTEM 'http://cbbc.murdoch.edu.au/dtd/baat.dtd'&gt; &lt;baat&gt; &lt;job toolPath='/usr/local/bin/blastall' toolName='blast'&gt; &lt;inputFile&gt;DQ6060.zip&lt;/inputFile&gt; &lt;outputFile&gt;1234567890.zip&lt;/outputFile&gt; &lt;parameterList&gt; &lt;parameter name='dataset' mandatory='Yes' switchOnly='No' switch='-d' value='nr' rank='1'/&gt; &lt;parameter name='dataset' mandatory='Yes' switchOnly='No' switch='-p' value='blastx' rank='2'/&gt; &lt;parameter name='dataset' mandatory='Yes' switchOnly='No' switch='-i' value='DQ6060.fa' rank='3'/&gt; &lt;parameter name='dataset' mandatory='Yes' switchOnly='No' switch='-d' value='nr' rank='4'/&gt; &lt;parameter name='dataset' mandatory='Yes' switchOnly='No' switch='-d' value='nr' rank='5'/&gt; &lt;parameter name='dataset' mandatory='Yes' switchOnly='No' switch='-d' value='nr' rank='6'/&gt; &lt;/parameterList&gt; &lt;grendel id='1234567'&gt; &lt;option&gt; &lt;name&gt;eric&lt;/name&gt; &lt;/option&gt; &lt;option&gt; &lt;name&gt;cache&lt;/name&gt; &lt;/option&gt; &lt;option&gt; &lt;name&gt;label&lt;/name&gt; &lt;value&gt;igrow&lt;/value&gt; &lt;/option&gt; &lt;/grendel&gt; &lt;priority&gt;-20&lt;/priority&gt; &lt;executionHost&gt;&lt;/executionHost&gt; &lt;batchNumber&gt;&lt;/batchNumber&gt; &lt;status&gt;&lt;/status&gt; &lt;startTime&gt;&lt;/startTime&gt; &lt;stopTime&gt;&lt;/stopTime&gt; &lt;submittedTime&gt;&lt;/submittedTime&gt; &lt;submitUser&gt;some user&lt;/submitUser&gt; &lt;submitLabel&gt;some_random_label&lt;/submitLabel&gt; &lt;/job&gt; &lt;/baat&gt;
</textarea>
<br/>
checkGrendel.input.jobId <input type="text" name="checkGrendel.input.jobId" value="derived(submitGrendel.output.jobId)"><br/>
submitGrendel.input.attachment <input type="text" size="40" name="submitGrendel.input.attachment" value="file:///export/home/tech/ntakayama/devel/ccg/yabi-mw/testdata/DQ6060.zip"><br/>
<input type="submit">
</form>
</body>
</html>
