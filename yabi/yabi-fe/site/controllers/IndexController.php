<?php
//$Id$

//Zend::loadClass('Zend_Controller_Action');
 
class IndexController extends Zend_Controller_Action {
	
    /**
     * indexAction
     */
    public function indexAction() {
    	$view = Zend::registry('view');
        $view->title = 'Dynamic Title';
        $view->body = 'This is a dynamic body.';        
        echo $view->render('example.php');
        
        /*
        $temp_file = 'homepage.htm';
        
        $view = Zend::registry('view');
        
        if (false === $view->isCached($temp_file))
        {
            $vars = array();
            $vars['title'  ] = 'Page <title>';
            $vars['text'   ] = 'A text is a text & a text is a text.';
            $vars['numbers'][0] = 12.9;
            $vars['numbers'][1] = 29;
            $vars['numbers'][2] = 78;
            
            $vars = $view->escape($vars);
            
            $view->assign($vars);
        }
        
        $view->output($temp_file);*/        
    }


    /**
     * noRouteAction
     */
    public function noRouteAction() {
        $this->_redirect('./');
    }
}
?>