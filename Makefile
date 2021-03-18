DATADIR=$(PWD)/ignored/data
TESTDATADIR=$(PWD)/testdata
TESTDATADIR_SEG_FAIL=$(PWD)/testdata-seg-fault

## devel
bash:
	docker-compose run --rm -v $(DATADIR):/data dev
run: cleandatatdir
	docker-compose run --rm -v $(DATADIR):/data dev

### testing
pytest:
	docker-compose run --rm app pytest
functest:
	docker-compose run --rm -v $(TESTDATADIR):/data app
seg-fail-test:
	docker-compose run --rm -v $(TESTDATADIR_SEG_FAIL):/data app; \
	if [ $$? -eq 1 ]; then \
		echo "Expected exit code 1 -> PASS"; \
	else \
		echo "Expected exit code 1 -> FAIL"; \
		exit 1; \
	fi
phptests:
	docker-compose run --rm app ./php/vendor/bin/phpunit -c ./php/phpunit.xml.dist
testall: pytest phptests seg-fail-test functest

##cleaning
rmi:
	-docker rmi -f  $$(docker images -q -f "dangling=true")
rm:
	-docker rm $$(docker ps -q -f 'status=exited')
clean:
	-docker rmi -f keboola/tde-exporter
cleandatatdir:
	-sudo rm -rf $(DATADIR)/out
cleantestdatadir:
	-sudo rm -rf $(TESTDATADIR)/out
cleanall: rmi clean rm
