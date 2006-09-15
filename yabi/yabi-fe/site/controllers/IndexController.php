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
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);

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
		
		$output = $view->getOutput();

        echo $output;
		
	}
	
	
	/**
     *noRouteAction
     */
	public function noRouteAction(){
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);
		$this->_redirect('./');
	}
}
?>