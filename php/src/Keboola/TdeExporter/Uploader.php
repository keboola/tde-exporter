<?php
namespace Keboola\TdeExporter;
use Symfony\Component\Finder\Finder;


/**
 * Class Uploader
 *
 */
class Uploader
{
    /**
     * @var Client
     */
    protected $client;
    /**
     * @var
     */
    protected $format = 'yaml';

    /**
     * @return mixed
     */
    public function getFormat()
    {
        return $this->format;
    }

    /**
     * @return Client
     */
    public function getClient()
    {
        return $this->client;
    }


    /**
     * @param Client $client
     */
    public function __construct(Client $client)
    {
        $this->setClient($client);
    }

    /**
     * @param $dir
     * @return array
     */
    protected function getManifestFiles($dir)
    {
        $finder = new Finder();
        $manifests = $finder->files()->name("*.manifest")->in($dir);
        $manifestNames = [];
        /** @var SplFileInfo $manifest */
        foreach ($manifests as $manifest) {
            $manifestNames[] = $manifest->getPathname();
        }
        return $manifestNames;
    }

    /**
     * Upload files from local temp directory to Storage.
     *
     * @param string $source Source path.
     * @param array $configurations Upload configurations.
     */
    public function uploadFiles($source, $configurations = array())
    {
        $manifestNames = $this->getManifestFiles($source);
        $finder = new Finder();
        /** @var SplFileInfo[] $files */
        $files = $finder->files()->notName("*.manifest")->in($source);
        $outputMappingFiles = array();
        foreach ($configurations as $config) {
            $outputMappingFiles[] = $config["source"];
        }
        $outputMappingFiles = array_unique($outputMappingFiles);
        $processedOutputMappingFiles = array();
        $fileNames = [];
        foreach ($files as $file) {
            $fileNames[] = $file->getFilename();
        }
        // Check if all files from output mappings are present
        foreach ($configurations as $config) {
            if (!in_array($config["source"], $fileNames)) {
                //throw new MissingFileException("File '{$config["source"]}' not found.");
                throw new \Excpetion("File '{$config["source"]}' not found.");
            }
        }
        // Check for manifest orphans
        foreach ($manifestNames as $manifest) {
            if (!in_array(substr(basename($manifest), 0, -9), $fileNames)) {
                //throw new ManifestMismatchException("Found orphaned file manifest: '" . basename($manifest) . "'");
                throw new \Excpetion("Found orphaned file manifest: '" . basename($manifest) . "'");
            }
        }
        foreach ($files as $file) {
            $configFromMapping = array();
            $configFromManifest = array();
            foreach ($configurations as $config) {
                if (isset($config["source"]) && $config["source"] == $file->getFilename()) {
                    $configFromMapping = $config;
                    $processedOutputMappingFiles[] = $configFromMapping["source"];
                    unset($configFromMapping["source"]);
                }
            }
            $manifestKey = array_search($file->getPathname() . ".manifest", $manifestNames);
            if ($manifestKey !== false) {
                $configFromManifest = $this->readFileManifest($file->getPathname() . ".manifest");
                unset($manifestNames[$manifestKey]);
            }
            try {
                // Mapping with higher priority
                if ($configFromMapping || !$configFromManifest) {
                    $storageConfig = (new File\Manifest())->parse(array($configFromMapping));
                } else {
                    $storageConfig = (new File\Manifest())->parse(array($configFromManifest));
                }
            } catch (InvalidConfigurationException $e) {
                //throw new UserException("Failed to write manifest for table {$file->getFilename()}.", $e);
                throw new \Exception("Failed to write manifest for table {$file->getFilename()}.", $e);
            }
            try {
                $this->uploadFile($file->getPathname(), $storageConfig);
            } catch (ClientException $e) {
                //throw new UserException(
                throw new \Exception(
                    "Cannot upload file '{$file->getFilename()}' to Storage API: " . $e->getMessage(),
                    $e
                );
            }
        }
        $processedOutputMappingFiles = array_unique($processedOutputMappingFiles);
        $diff = array_diff(
            array_merge($outputMappingFiles, $processedOutputMappingFiles),
            $processedOutputMappingFiles
        );
        if (count($diff)) {
            //throw new UserException("Couldn't process output mapping for file(s) '" . join("', '", $diff) . "'.");
            throw new \Exception("Couldn't process output mapping for file(s) '" . join("', '", $diff) . "'.");
        }
    }


 /**
     * @param $source
     * @return array
     */
    protected function readFileManifest($source)
    {
        $adapter = new File\Manifest\Adapter($this->getFormat());
        try {
            return $adapter->readFromFile($source);
        } catch (\Exception $e) {
            //throw new ManifestMismatchException(
            throw new \Exception(
                "Failed to parse manifest file $source as " . $this->getFormat() . " " . $e->getMessage(),
                $e
            );
        }
    }
    /**
     * @param $source
     * @param array $config
     * @throws \Keboola\StorageApi\ClientException
     */
    protected function uploadFile($source, $config = array())
    {
        $options = new FileUploadOptions();
        $options
            ->setTags(array_unique($config["tags"]))
            ->setIsPermanent($config["is_permanent"])
            ->setIsEncrypted($config["is_encrypted"])
            ->setIsPublic($config["is_public"])
            ->setNotify($config["notify"]);
        $this->getClient()->uploadFile($source, $options);
    }
}