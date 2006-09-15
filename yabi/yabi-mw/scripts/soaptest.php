<?php
$client = new SoapClient("http://boromir.localdomain:8080/axis/services/yabiws?wsdl");
try {
    //$pdf = $client->convertFO2PDF($fo);
} catch (SoapFault $e) {
    echo $e;
}

//echo base64_encode($fo);

//file_put_contents('result.encoded.txt', $pdf);
//file_put_contents('result.pdf', base64_decode($pdf));
?>
