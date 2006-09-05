<?php
// $Id: index.php,v 1.1 2006/07/11 05:20:24 andrew Exp $

// set include path
$include_path = ini_get('include_path');
ini_set('include_path', $include_path . ':/usr/local/php5/lib/php/ZendFramework');
define("APP_ROOT", "#approot#");

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

?>