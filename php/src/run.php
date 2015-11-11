<?php
/**
 * @package tde-uploader
 * @copyright 2015 Keboola
 * @author Tomasko Kacur <tomas.kacur@keboola.com>
 */

use Symfony\Component\Yaml\Yaml;
use Keboola\StorageApi\Client;
use Keboola\TdeExporter\Uploader;

$filesPath = "/data/tde-files";


set_error_handler(
    function ($errno, $errstr, $errfile, $errline, array $errcontext) {
        if (0 === error_reporting()) {
            return false;
        }
        throw new ErrorException($errstr, 0, $errno, $errfile, $errline);
    }
);

require_once(dirname(__FILE__) . "/../vendor/autoload.php");
//var_dump($argv);

//$token = getenv('KBC_TOKEN');
if (count($argv) < 2) {
    print 'php-uploader error: kbc token not provided';
    exit(1);
}

$token = $argv[1];
if (empty($token)) {
    print 'php-uploader error: kbc token not provided or missing';
    exit(1);
}

$sapiClient = new Client([
    'token' => $token,
]);

// set run id
$runId = '';
if (count($argv) > 2) {
    $runId = $argv[2];

}

$sapiClient->setRunId($runId);

$uploader = new Uploader($sapiClient);

try {
    $uploader->uploadFiles($filesPath);
} catch (\Exception $e) {
    print $e->getMessage();
    exit(1);
}

exit(0);
