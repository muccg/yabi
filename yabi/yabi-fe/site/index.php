<?php
// $Id$

// set include path
$include_path = ini_get('include_path');
ini_set('include_path', $include_path . ':/usr/local/php5/lib/php/ZendFramework');
define("APP_ROOT", "#approot#");

require_once('Zend.php');
require_once('Zend/Log.php');// Zend_Log base class
require_once('Zend/Log/Adapter/File.php');   // File log adapter
require_once('Zend/Log.php');                // Zend_Log base class
require_once('Zend/Log/Adapter/File.php');   // File log adapter
require_once('Zend/Config.php');
require_once('Zend/Config/Array.php');
require_once('smarty/Smarty.class.php');
require_once(APP_ROOT . '/models/Ccg_View_Smarty.php');


/**
 * __autoload
 */
function __autoload($class) {
    Zend::loadClass($class);
}


try {

    // Register the file logger
    Zend_Log::registerLogger(new Zend_Log_Adapter_File(APP_ROOT.'/logs/log.txt'));
    Zend_Log::log('============================================================');
    
    
    // munge incoming URI to remove subdirectories
    $_SERVER['REQUEST_URI'] = preg_replace('/^' . preg_quote(dirname($_SERVER['PHP_SELF']), '/') . '/', '', $_SERVER['REQUEST_URI']);


    // config data
    $config['ZF_S'] = array(
                            //	'webhost' => 'www.example.com',
                            'smarty' => array(
                                              'template_dir' => APP_ROOT.'/templates',
                                              'compile_dir' => APP_ROOT.'/compile',
                                              'cache_dir' => APP_ROOT.'/cache',
                                              'caching' => true
                                              //		'cache_lifetime' => APP_ROOT.'/cache_lifetime',
                                              //		'config_dir' => APP_ROOT.'/config_dir'
                                              )
                            );

    // config file
    $config = new Zend_Config($config);
    Zend::register('config', $config);


    // Zend view & Smarty
    $viewConfig = array();
    $viewConfig['scriptPath'] = APP_ROOT.'/templates';

    $view = new Ccg_View_Smarty($viewConfig);
    Zend::register('view', $view);


    // get controller
    $controller = Zend_Controller_Front::getInstance();
    $controller->setControllerDirectory(APP_ROOT.'/controllers/');
    $controller->dispatch();


} catch (Exception $e) {
    
// Print out message to client
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>YABI-fe Error</title>
<!--<link rel="stylesheet" type="text/css" href="css/pager.css" /> -->
<!--<link rel="stylesheet" type="text/css" href="css/gemmtools.css" /> -->
</head>
<body>
<div id="Content">
<h2>A serious error has occured.</h2> 
<p/> The following error will be automatically reported to the System Administrator:
<pre style="color: black; background-color: #EEEEEE;">

<?php
echo 'Error: ' . $e->getMessage() . "\n";
echo 'File: ' . $e->getFile() . "\n";
echo 'Line: ' . $e->getLine() . "\n\n";
echo $e->getTraceAsString();
?>

</pre>

If you feel it is necessary you can contact the [<a href="mailto:techs@ccg.murdoch.edu.au?subject=YABI-fe User Error Report&body=YABI-fe%20User%20Error%20Report:%0A%0AModule:%0A%0AAction:%0A%0ADescription of Error:%0A">System Administrator (techs@ccg.murdoch.edu.au)</a>] via email.<br>
<br/>
Click <a href="index.php">here</a> to continue using YABI-fe.
</div><br/><br/><br/><br/><br/><br/>
<div id="footer">
&copy; Copyright Murdoch University 2005, 2006
</div>
</body>
</html>
<?php
exit();
}
?>