<?php

    $definitionId = 1;

    // check service for xml, add to db
    $params = http_build_query(array('id'  => $definitionId,
                                     'delay1.input.delay' => '120000',
                                     'delay2.input.delay' => '120000',
                                     'delay3.input.delay' => '120000',
                                     'delay1.input.param 1' => 'test',
                                     'delay2.input.param 1' => 'test',
                                     'delay3.input.param 1' => 'test'
                                     )
                               );

    $options = array('http' => array(
                                     'method' => 'POST',
                                     'content' => $params,
                                     'header' => 'Content-type:application/x-www-form-urlencoded'
                                     )
                     );

    $context = stream_context_create($options);
    $contents = @file_get_contents('http://boromir.localdomain:8080/yabi-ntakayama/instantiate.ws', false, $context); // @ suppresses warning so we can throw exception instead if a problem

    echo $contents;
?>
