<?php
namespace Keboola\TdeExporter\Tests;
use Keboola\TdeExporter\Uploader;
use Keboola\TdeExporter\Configuration;
use Keboola\TdeExporter\Manifest;
use Keboola\Temp\Temp;
use Symfony\Component\Filesystem\Filesystem;
use Keboola\StorageApi\Client;
use Keboola\StorageApi\Options\FileUploadOptions;
use Keboola\StorageApi\Options\ListFilesOptions;

class UploaderTest extends \PHPUnit_Framework_TestCase
{
    /**
     * @var Client
     */
    protected $client;
    /**
     * @var Temp
     */
    private $tmp;
    /**
     * @throws \Exception
     * @throws \Keboola\StorageApi\ClientException
     */
    protected function clearBucket()
    {
        // Delete tables and bucket
        if ($this->client->bucketExists("out.c-tde-test")) {
            foreach ($this->client->listTables("out.c-tde-test") as $table) {
                $this->client->dropTable($table["id"]);
            }
            // Delete bucket
            $this->client->dropBucket("out.c-tde-test");
        }
    }
    /**
     *
     */
    protected function clearFileUploads()
    {
        // Delete file uploads
        $options = new ListFilesOptions();
        $options->setTags(array("tde-exporter-php-test"));
        sleep(1);
        $files = $this->client->listFiles($options);
        foreach ($files as $file) {
            $this->client->deleteFile($file["id"]);
        }
    }
    /**
     *
     */
    public function setUp()
    {
        // Create folders
        $this->tmp = new Temp();
        $this->tmp->initRunFolder();
        $root = $this->tmp->getTmpFolder();
        $fs = new Filesystem();
        $fs->mkdir($root . DIRECTORY_SEPARATOR . "upload");
        $fs->mkdir($root . DIRECTORY_SEPARATOR . "download");
        $this->client = new Client(array("token" => STORAGE_API_TOKEN));
        $this->clearBucket();
        $this->clearFileUploads();
    }
    /**
     *
     */
    public function tearDown()
    {
        // Delete local files
        $this->tmp = null;
        $this->clearBucket();
        $this->clearFileUploads();
    }


    /**
     * @throws \Keboola\StorageApi\ClientException
     */
    public function testWriteFiles()
    {
        $root = $this->tmp->getTmpFolder();
        file_put_contents($root . "/upload/file1", "test");
        file_put_contents($root . "/upload/file2", "test");
        file_put_contents(
            $root . "/upload/file2.manifest",
            "tags: [\"tde-exporter-php-test\", \"xxx\"]\nis_public: false"
        );
        file_put_contents($root . "/upload/file3", "test");
        file_put_contents($root . "/upload/file3.manifest", "tags: [\"tde-exporter-php-test\"]\nis_public: true");
        $configs = array(
            array(
                "source" => "file1",
                "tags" => array("tde-exporter-php-test")
            ),
            array(
                "source" => "file2",
                "tags" => array("tde-exporter-php-test", "another-tag"),
                "is_public" => true
            )
        );
        $writer = new Uploader($this->client);
        $writer->uploadFiles($root . "/upload", $configs);
        $options = new ListFilesOptions();
        $options->setTags(array("tde-exporter-php-test"));
        sleep(1);
        $files = $this->client->listFiles($options);
        $this->assertCount(3, $files);
        $file1 = $file2 = $file3 = null;
        foreach ($files as $file) {
            if ($file["name"] == 'file1') {
                $file1 = $file;
            }
            if ($file["name"] == 'file2') {
                $file2 = $file;
            }
            if ($file["name"] == 'file3') {
                $file3 = $file;
            }
        }
        $this->assertNotNull($file1);
        $this->assertNotNull($file2);
        $this->assertNotNull($file3);
        $this->assertEquals(4, $file1["sizeBytes"]);
        $this->assertEquals(array("tde-exporter-php-test"), $file1["tags"]);
        $this->assertEquals(array("tde-exporter-php-test", "another-tag"), $file2["tags"]);
        $this->assertEquals(array("tde-exporter-php-test"), $file3["tags"]);
        $this->assertFalse($file1["isPublic"]);
        $this->assertTrue($file2["isPublic"]);
        $this->assertTrue($file3["isPublic"]);
    }

     /**
     * @throws \Keboola\StorageApi\ClientException
     */
    public function testWriteFilesOutputMapping()
    {
        $root = $this->tmp->getTmpFolder();
        file_put_contents($root . "/upload/file1", "test");
        $configs = array(
            array(
                "source" => "file1",
                "tags" => array("tde-exporter-php-test")
            )
        );
        $writer = new Uploader($this->client);
        $writer->uploadFiles($root . "/upload", $configs);
        $options = new ListFilesOptions();
        $options->setTags(array("tde-exporter-php-test"));
        sleep(1);
        $files = $this->client->listFiles($options);
        $this->assertCount(1, $files);
        $file1 = null;
        foreach ($files as $file) {
            if ($file["name"] == 'file1') {
                $file1 = $file;
            }
        }
        $this->assertNotNull($file1);
        $this->assertEquals(4, $file1["sizeBytes"]);
        $this->assertEquals(array("tde-exporter-php-test"), $file1["tags"]);
    }


  /**
     */
    public function testWriteFilesOutputMappingAndManifest()
    {
        $root = $this->tmp->getTmpFolder();
        file_put_contents($root . "/upload/file1", "test");
        file_put_contents($root . "/upload/file1.manifest", "tags: [\"tde-exporter-php-test\", \"xxx\"]\nis_public: true");
        $configs = array(
            array(
                "source" => "file1",
                "tags" => array("tde-exporter-php-test", "yyy"),
                "is_public" => false
            )
        );
        $writer = new Uploader($this->client);
        $writer->uploadFiles($root . "/upload", $configs);
        $options = new ListFilesOptions();
        $options->setTags(array("tde-exporter-php-test"));
        sleep(1);
        $files = $this->client->listFiles($options);
        $this->assertCount(1, $files);
        $file1 = null;
        foreach ($files as $file) {
            if ($file["name"] == 'file1') {
                $file1 = $file;
            }
        }
        $this->assertNotNull($file1);
        $this->assertEquals(4, $file1["sizeBytes"]);
        $this->assertEquals(array("tde-exporter-php-test", "yyy"), $file1["tags"]);
        $this->assertFalse($file1["isPublic"]);
    }


    public function testWriteFilesInvalidYaml()
    {
        $root = $this->tmp->getTmpFolder();
        file_put_contents($root . "/upload/file1", "test");
        file_put_contents($root . "/upload/file1.manifest", "\tthis is not \n\t \tat all a {valid} yaml");
        $configs = array(
            array(
                "source" => "file1",
                "tags" => array("tde-exporter-php-test", "yyy"),
                "is_public" => false
            )
        );
        $writer = new Uploader($this->client);
        $writer->setFormat('yaml');
        try {
            $writer->uploadFiles($root . "/upload", $configs);
            $this->fail("Invalid manifest must raise exception.");
        } catch (\Exception $e) {
            $this->assertContains('yaml', $e->getMessage());
        }
    }


    /**
     * @expectedException \Exception
     * @expectedExceptionMessage File 'file2' not found
     */
    public function testWriteFilesOutputMappingMissing()
    {
        $root = $this->tmp->getTmpFolder();
        file_put_contents($root . "/upload/file1", "test");
        file_put_contents($root . "/upload/file1.manifest", "tags: [\"tde-exporter-php-test-xxx\"]\nis_public: true");
        $configs = array(
            array(
                "source" => "file2",
                "tags" => array("tde-exporter-php-test"),
                "is_public" => false
            )
        );
        $writer = new Uploader($this->client);
        $writer->uploadFiles($root . "/upload", $configs);
    }
    /**
     * @expectedException \Exception
     * @expectedExceptionMessage Found orphaned file manifest: 'file1.manifest'
     */
    public function testWriteFilesOrphanedManifest()
    {
        $root = $this->tmp->getTmpFolder();
        file_put_contents($root . "/upload/file1.manifest", "tags: [\"tde-exporter-php-test-xxx\"]\nis_public: true");
        $writer = new Uploader($this->client);
        $writer->uploadFiles($root . "/upload");
    }


}