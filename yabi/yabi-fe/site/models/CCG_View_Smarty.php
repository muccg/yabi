<?php
  /**
   * @version $Id$
   * @package yabi
   * @copyright CCG, Murdoch University, 2006.
   */

  /**
   * CCG_View_Smarty
   * @package yabi
   */
class CCG_View_Smarty extends Zend_View_Abstract {

    /** @var $smarty */
	private $smarty = false;

    /** @var $render */
	private $render = true; // if true will display else fetch

    /** @var $output */
	private $output;
		

    /**
     * __construct
     */
	public function __construct($viewConfig = array()) {
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);
		
        // get config
		$config = Zend::registry('config');

        // set up scriptpath
        $viewConfig['scriptPath'] = $config->smarty->template_dir;
		parent::__construct($viewConfig);
		
        // set up smarty
		$this->smarty = new Smarty();
		$this->smarty->caching =  $config->smarty->caching;
		$this->smarty->cache_lifetime =  $config->smarty->cache_lifetime;
		$this->smarty->template_dir = $config->smarty->template_dir;
		$this->smarty->compile_dir = $config->smarty->compile_dir;
		$this->smarty->config_dir =  $config->smarty->config_dir;
		$this->smarty->cache_dir = $config->smarty->cache_dir;
	}
	
	
	/**
	 * run
	 */
	protected function _run($template) {		
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);

		if($this->render == true) {
			$this->smarty->display($template);
		} else {
			$this->output = $this->smarty->fetch($template);
		}
	}

	
	/**
	 * setRender
	 */
	public function setRender($value) {
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);
        $this->render = $value;
	}

	
	/**
	 * getOutput
	 */
	public function getOutput() {
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);
		return $this->output;	
	} 


	/**
	 * assign
	 */
	public function assign($var) {
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);

		if(is_string($var)) {
			$value = @func_get_arg(1);
            $this->smarty->assign($var, $value);
		} elseif(is_array($var)) {
			foreach($var as $key => $value) {
				$this->smarty->assign($key, $value);
			}
		} else {
			throw new Zend_View_Exception('assign() expects a string or array, got '.gettype($var));
		}
	}


	/**
	 * escape
	 */	
	public function escape($var) {
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);

		if(is_string($var)) {
			return parent::escape($var);
		} elseif(is_array($var)) {
			foreach ($var as $key => $val) {
				$var[$key] = $this->escape($val);
			}
			return $var;
		} else {
			return $var;
		}
	}
	
	
	/**
	 * output
	 */
	public function output($name) {
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);

		//header("Expires: Mon, 26 Jul 1997 05:00:00 GMT");
		//header("Cache-Control: no-cache");
		//header("Pragma: no-cache");
		//header("Cache-Control: post-check=0, pre-check=0", FALSE);

		print parent::render($name);
	}
	
	
	/**
	 * isCached
	 */
	public function isCached($template) {
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);

		if ($this->smarty->is_cached($template)) {
			return true;
		}
		return false;
	}


	/**
     * setCaching
     */
	public function setCaching($caching) {
        Zend_Log::log(__CLASS__ .':'. __FUNCTION__ .':' . __LINE__);
		$this->smarty->caching = $caching;
	}

}
?>