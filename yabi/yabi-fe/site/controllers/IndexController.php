<?php
//$Id$

//Zend::loadClass('Zend_Controller_Action');

class IndexController extends Zend_Controller_Action {
	
	
	/**
	*indexAction
	*/
	public function indexAction(){
	
		$temp_file='index.tpl';
		
		$view=Zend::registry('view');
		
		if(false===$view->isCached($temp_file)){
			$vars=array();
			$vars['title']='Hello!!!';
			$vars['text']='A text is a text & a text is a text.';
			//not in index.tpl yet.
		/*	$vars['numbers'][0]=12.9;
			$vars['numbers'][1]=29;
			$vars['numbers'][2]=78;*/
			
			$vars=$view->escape($vars);
			
			
			
			$view->assign($vars);
			
			$view->setRender(0);
		}
		
		$view->output($temp_file);
		
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