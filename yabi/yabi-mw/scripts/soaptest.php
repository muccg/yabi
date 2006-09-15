<?php
$client = new SoapClient("http://boromir.localdomain:8080/axis-ntakayama/services/yabiws?wsdl");
try {
    $result = $client->isAlive();
} catch (SoapFault $e) {
    echo $e;
}

echo $result;
?>
