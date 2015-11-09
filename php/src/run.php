<?php
/**
 * @package tde-uploader
 * @copyright 2015 Keboola
 * @author Tomasko Kacur <tomas.kacur@keboola.com>
 */

use Symfony\Component\Yaml\Yaml;
use Keboola\StorageApi\Client;
use Keboola\TdeExporter\Uploader;

$filesPath = "/data/out/tables";


set_error_handler(
    function ($errno, $errstr, $errfile, $errline, array $errcontext) {
        if (0 === error_reporting()) {
            return false;
        }
        throw new ErrorException($errstr, 0, $errno, $errfile, $errline);
    }
);

require_once(dirname(__FILE__) . "/../vendor/autoload.php");

$token = getenv('KBC_TOKEN');
if (empty($token)) {
    print 'KBC_TOKEN env variable not set.';
    exit(1);
}

$sapiClient = new Client([
    'token' => $token,
]);

// set run id
$runId = getenv('KBC_RUNID');
if (empty($runId)) {
    $runId = '';
}
$sapiClient->setRunId($runId);

$uploader = new Uploader($sapiClient);

try {
    $uploader->uploadFiles($filesPath);
} catch (\Excpetion $e) {
    print $e->getMessage();
    exit(-1);
}

exit(0);
