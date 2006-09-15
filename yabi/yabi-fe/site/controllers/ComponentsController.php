<?php
  /**
   * @version $Id$
   * @package yabi
   * @copyright CCG, Murdoch University, 2006.
   */

  /**
   * ComponentsController
   * @package yabi
   */
class ComponentsController extends CCGController {

	
    /**
     * indexAction
     */
	public function indexAction(){
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);

	
	}


    /**
     * componentAAction
     */
	public function componentAAction(){
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);

        $isComponent = false;
        if($this->_getParam('isComponent') === true) {
            $isComponent = true;
        }


		$template='A.tpl';
		
		$view=Zend::registry('view');
		
		if(false === $view->isCached($template)){
			$vars = array();
			$vars['text'] = 'You are at componentA action!';

			$vars = $view->escape($vars);
			$view->assign($vars);
		}



        if($isComponent) {
            $view->setRender(false);
            $view->output($template);
            $output = $view->getOutput();

        } else {
            $view->output($template);
        }
		
		
        if(Zend::isRegistered('actionChain')) {
            $actionChain = Zend::registry('actionChain');
            if($actionChain->hasLinks()) {
                $forward = $actionChain->getLink();
                $this->_forward($forward['controller'], $forward['action']);
            }
        }
		
	}


    /**
     * componentBAction
     */
	public function componentBAction(){
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);

		$template='A.tpl';
		
		$view=Zend::registry('view');
		
		if(false === $view->isCached($template)){
			$vars = array();
			$vars['text'] = 'You are at componentB action!';

			$vars = $view->escape($vars);
			$view->assign($vars);
			
		}
		
		$view->output($template);
		
		$output = $view->getOutput();

        echo $output;

        if(Zend::isRegistered('actionChain')) {
            $actionChain = Zend::registry('actionChain');
            if($actionChain->hasLinks()) {
                $forward = $actionChain->getLink();
                $this->_forward($forward['controller'], $forward['action']);
            }
        }
		
	}


    /**
     * componentCAction
     */
	public function componentCAction(){
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);

		$template='A.tpl';
		
		$view=Zend::registry('view');
		
		if(false === $view->isCached($template)){
			$vars = array();
			$vars['text'] = 'You are at componentC action!';

			$vars = $view->escape($vars);
			$view->assign($vars);
			
		}
		
		$view->output($template);
		
		$output = $view->getOutput();

        echo $output;

        if(Zend::isRegistered('actionChain')) {
            $actionChain = Zend::registry('actionChain');
            if($actionChain->hasLinks()) {
                $forward = $actionChain->getLink();
                $this->_forward($forward['controller'], $forward['action']);
            }
        }

		
	}




	
}
?>