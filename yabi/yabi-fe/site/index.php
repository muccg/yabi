<?php
// $Id: index.php,v 1.1 2006/07/11 05:20:24 andrew Exp $

// set include path
$include_path = ini_get('include_path');
ini_set('include_path', $include_path . ':/usr/local/php5/lib/php/ZendFramework');


// require files
require_once('Zend.php');
Zend::loadClass('Zend_Controller_Front');

require_once 'Zend/Log.php';                // Zend_Log base class
require_once 'Zend/Log/Adapter/File.php';   // File log adapter


// Register the file logger
Zend_Log::registerLogger(new Zend_Log_Adapter_File('logs/log.txt'));
Zend_Log::log('============================================================');


// munge incoming URI to remove subdirectories
$_SERVER['REQUEST_URI'] = preg_replace('/^' . preg_quote(dirname($_SERVER['PHP_SELF']), '/') . '/', '', $_SERVER['REQUEST_URI']);

// get controller
$controller = Zend_Controller_Front::getInstance();
$controller->setControllerDirectory('controllers/');
$controller->dispatch();

?>