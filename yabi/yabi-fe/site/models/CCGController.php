<?php
  /**
   * @version $Id$
   * @package yabi
   * @copyright CCG, Murdoch University, 2006.
   */

  /**
   * CCGController
   * @package yabi
   */
abstract class CCGController extends Zend_Controller_Action {

    /** @var $render */
    private $render = true;


    /**
     * setRender
     */
    public function setRender($value) {
        $this->render = $value;
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