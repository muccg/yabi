<?php

    $delaydefinition = '<process-definition name="delay">
        <start-state name="start">
          <transition to="delay" />
        </start-state>
        <node name="delay">
          <action class="au.edu.murdoch.ccg.yabi.actions.JBPMDelay" />
          <transition to="end" name="next" />
        </node>
        <end-state name="end" />
      </process-definition>';

    $forkdelaydefinition = '<process-definition name="forkdelay">
        <start-state name="start">
          <transition to="fork" />
        </start-state>
        <fork name="fork">
          <transition name="left" to="delay1" />
          <transition name="right" to="delay2" />
        </fork>
        <state name="delay1">
          <timer duedate="2 seconds">
            <action class="au.edu.murdoch.ccg.yabi.actions.JBPMDelay" />
          </timer>
          <transition name="next" to="join"/>
        </state>
        <state name="delay2">
          <timer duedate="2 seconds">
            <action class="au.edu.murdoch.ccg.yabi.actions.JBPMDelay" />
          </timer>
          <transition to="join" name="next" />
        </state>
        <join name="join">
          <transition to="delay3" />
        </join>
        <state name="delay3">
          <timer duedate="2 seconds">
            <action class="au.edu.murdoch.ccg.yabi.actions.JBPMDelay" />
          </timer>
          <transition to="end" name="next" />
        </state>
        <end-state name="end" />
      </process-definition>';

    $timerlessforkdef = '<process-definition name="forkdelay">
        <start-state name="start">
          <transition to="fork" />
        </start-state>
        <fork name="fork">
          <transition name="left" to="delay1" />
          <transition name="right" to="delay2" />
        </fork>
        <node name="delay1">
          <action class="au.edu.murdoch.ccg.yabi.actions.JBPMDelay" />
          <transition name="next" to="join"/>
        </node>
        <node name="delay2">
          <action class="au.edu.murdoch.ccg.yabi.actions.JBPMDelay" />
          <transition to="join" name="next" />
        </node>
        <join name="join">
          <transition to="delay3" />
        </join>
        <node name="delay3">
          <action class="au.edu.murdoch.ccg.yabi.actions.JBPMDelay" />
          <transition to="end" name="next" />
        </node>
        <end-state name="end" />
      </process-definition>';

    $definition = $timerlessforkdef;

    // check service for xml, add to db
    $params = http_build_query(array('definition'  => $definition
                                     )
                               );

    $options = array('http' => array(
                                     'method' => 'POST',
                                     'content' => $params,
                                     'header' => 'Content-type:application/x-www-form-urlencoded'
                                     )
                     );

    $context = stream_context_create($options);
    $contents = @file_get_contents('http://boromir.localdomain:8080/yabi-ntakayama/deploy.ws', false, $context); // @ suppresses warning so we can throw exception instead if a problem

    echo $contents;
?>
