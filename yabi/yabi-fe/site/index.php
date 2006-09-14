<?php
// $Id: index.php,v 1.1 2006/07/11 05:20:24 andrew Exp $

// set include path
$include_path = ini_get('include_path');
ini_set('include_path', $include_path . ':/usr/local/php5/lib/php/ZendFramework');
define("APP_ROOT", "#approot#");


try {

    // require file
    require_once('Zend.php');
    
    function __autoload($class)
    {
        Zend::loadClass($class);
    }
    
    require_once('Zend/Log.php');                // Zend_Log base class
    require_once('Zend/Log/Adapter/File.php');   // File log adapter
    
    
    // Register the file logger
    Zend_Log::registerLogger(new Zend_Log_Adapter_File(APP_ROOT.'/logs/log.txt'));
    Zend_Log::log('============================================================');
    
    
    // munge incoming URI to remove subdirectories
    $_SERVER['REQUEST_URI'] = preg_replace('/^' . preg_quote(dirname($_SERVER['PHP_SELF']), '/') . '/', '', $_SERVER['REQUEST_URI']);
    
    // Zend View Register
    $view = new Zend_View;
    $view->setScriptPath(APP_ROOT.'/views');
    Zend::register('view', $view);
    /*
    // Smarty
    $viewConfig = array();
    $viewConfig[APP_ROOT.'/views'] = $config->getSetting('framework', 'view_dir');
    $view = new Travello_View_Smarty($viewConfig);
    Zend::register('view', $view);*/
    
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
    echo $e->getMessage();
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