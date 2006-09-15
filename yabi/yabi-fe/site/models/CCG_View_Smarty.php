<?php

class CCG_View_Smarty extends Zend_View_Abstract
{
	private $_smarty = false;
	private $_render = true; // if true will display else fetch
	private $output;
		
	/**
	 * Default Constructor
	 */
	public function __construct($data = array()) {
		
		$config = Zend::registry('config');
		parent::__construct($data);
		
		$this->_smarty = new Smarty();
		
		//$this->_smarty->caching =  $config->ZF_S->smarty->caching;
		//$this->_smarty->cache_lifetime =  $config->ZF_S->smarty->cache_lifetime;
		$this->_smarty->template_dir = $config->ZF_S->smarty->template_dir;
		$this->_smarty->compile_dir = $config->ZF_S->smarty->compile_dir;
		//$this->_smarty->config_dir =  $config->ZF_S->smarty->config_dir;
		$this->_smarty->cache_dir = $config->ZF_S->smarty->cache_dir;
	}
	
	
	/**
	 * run
	 */
	protected function _run($template) {		
		if($this->_render == true) {
			$this->_smarty->display($template);
		}
		else {
			$this->output = $this->_smarty->fetch($template);
			// this will return nothing >>  return $this->output;		
		}
	}
	
	/**
	 * setRender
	 */
	public function setRender($value) {
		if(($value == true || $value == false))	{
			$this->_render = $value;
		}
	}
	
	/**
	 * getOutput
	 */
	public function getOutput()
	{
		return $this->output;	
	} 
	
	/**
	 * assign
	 */
	public function assign($var) {
		if(is_string($var)) {
			$value = @func_get_arg(1);
			
			$this->_smarty->assign($var, $value);
		}
		elseif(is_array($var))	{
			foreach($var as $key => $value) {
				$this->_smarty->assign($key, $value);
			}
		}
		else {
			throw new Zend_View_Exception('assign() expects a string or array, got '.gettype($var));
		}
	}
		
	
	/**
	 * escape
	 */	
	public function escape($var) {
		if(is_string($var)) {
			return parent::escape($var);
		}
		elseif(is_array($var))	{
			foreach ($var as $key => $val) {
				$var[$key] = $this->escape($val);
			}

			return $var;
		}
		else {
			return $var;
		}
	}
	
	
	/**
	 * output
	 */
	public function output($name) {
		header("Expires: Mon, 26 Jul 1997 05:00:00 GMT");
		header("Cache-Control: no-cache");
		header("Pragma: no-cache");
		header("Cache-Control: post-check=0, pre-check=0", FALSE);

		print parent::render($name);
	}
	
	
	/**
	 * isCached
	 */
	public function isCached($template) {
		if ($this->_smarty->is_cached($template)) {
			return true;
		}
		
		return false;
	}


	/**
 	* setCaching
 	*/
	public function setCaching($caching) {
		$this->_smarty->caching = $caching;
	}

}
?>
				