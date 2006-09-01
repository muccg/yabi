<?php
//$Id$

Zend::loadClass('Zend_Controller_Action');
 
class IndexController extends Zend_Controller_Action {
	
    /**
     * indexAction
     */
    public function indexAction() {
        echo "You have reached the index action";	
    }


    /**
     * noRouteAction
     */
    public function noRouteAction() {
        echo "Unknown controller and action.";
    }
}
?>