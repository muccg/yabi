<?php
  /**
   * @version $Id$
   * @package yabi
   * @copyright CCG, Murdoch University, 2006.
   */

  /**
   * IndexController
   * @package yabi
   */
class IndexController extends Zend_Controller_Action {

	/**
     *indexAction
     */
	public function indexAction(){
	
		$template='index.tpl';
		
		$view=Zend::registry('view');
		
		if(false === $view->isCached($template)){
			$vars = array();
			$vars['title'] = 'Hello!!!';
			$vars['text'] = 'A text is a text & a text is a text.';


			$vars = $view->escape($vars);
			$view->assign($vars);
			
			$view->setRender(false);
		}
		
		$view->output($template);
		
		$output = $view->getOutput(); // i can't get the protected function output
		// to return the template as output
		
		echo "test". $output; // just to verify that it works 
		
	}
	
	
	/**
     *noRouteAction
     */
	public function noRouteAction(){
		$this->_redirect('./');
	}
}
?>