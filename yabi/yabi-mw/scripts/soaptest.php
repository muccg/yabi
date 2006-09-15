<?php
$client = new SoapClient("http://boromir.localdomain:8080/axis-ntakayama/services/yabiws?wsdl");
try {

$functions = $client->__getFunctions();
print_r($functions);
$types = $client->__getTypes();
print_r($types);

    $result = $client->isAlive();    
    $defs = $client->getDefinitions();

} catch (SoapFault $e) {
    echo $e;
}

echo "isAlive: " . $result . "\n";
echo "getDefinitions: " . $defs . "\n";
?>
