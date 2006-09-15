<?php
  /**
   * @version $Id$
   * @package yabi
   * @copyright CCG, Murdoch University, 2006.
   */

  /**
   * ActionChain
   * @package yabi
   */
class ActionChain {

    /** @var $links */
    private $links = array();

    /** @var $output */
    private $output = array();


    /**
     * register
     */
    public function addLink($controller, $action) {
        $this->links[] = array('controller' => $controller,
                               'action' => $action
                               );
    }

    public function getLink() {
        return array_shift($this->links);
    }

    public function hasLinks() {
        return (count($this->links) > 0);
    }


    /**
     * fetchOutput
     */
    public function fetchOutput($name) {



    }



	
}
?>