<?php
// Define path to application directory
define('ROOT_PATH', __DIR__);
// Ensure library/ is on include_path
/*
set_include_path(implode(PATH_SEPARATOR, array(
    realpath(ROOT_PATH . '/library'),
    get_include_path(),
)));
*/
ini_set('display_errors', true);
date_default_timezone_set('Europe/Prague');
if (file_exists(__DIR__ . '/config.php')) {
    require_once __DIR__ . '/config.php';
}
require_once ROOT_PATH . '/../vendor/autoload.php';
defined('STORAGE_API_TOKEN')
    || define('STORAGE_API_TOKEN', getenv('STORAGE_API_TOKEN') ? getenv('STORAGE_API_TOKEN') : 'your_token');