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
class IndexController extends CCGController {

	/**
     *indexAction
     */
	public function indexAction(){
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);


        $actionChain = new ActionChain();
        $actionChain->addLink('Components', 'componentA');
        $actionChain->addLink('Components', 'componentB');
        $actionChain->addLink('Components', 'componentC');
        $actionChain->addLink('Index', 'displayOutput');

        Zend::register('actionChain', $actionChain);


        $actionChain = Zend::registry('actionChain');
        $forward = $actionChain->getLink();
        $this->_forward($forward['controller'], $forward['action']);





// 		$template='index.tpl';
		
// 		$view=Zend::registry('view');
		
// 		if(false === $view->isCached($template)){
// 			$vars = array();
// 			$vars['title'] = 'Hello!!!';
// 			$vars['text'] = 'A text is a text & a text is a text.';


// 			$vars = $view->escape($vars);
// 			$view->assign($vars);
			
// 			$view->setRender($this->render);
// 		}
		
// 		$view->output($template);
		
// 		$output = $view->getOutput();

//         echo $output;
		
	}
	


    public function displayOutputAction() {

        $actionChain = Zend::registry('actionChain');
        echo 'You are at displayOutputAction!';


    }


}
?>