DATADIR=$(PWD)/ignored/data
TESTDATADIR=$(PWD)/testdata

## devel
bash:
	docker-compose run --rm -v $(DATADIR):/data dev
run: cleandatatdir
	docker-compose run --rm -v $(DATADIR):/data dev

### testing
pytest:
	docker-compose run --rm app pytest
functest: cleantestdatadir
	docker-compose run --rm -v $(TESTDATADIR):/data app
testall: pytest functest

##cleaning
rmi:
	docker rmi -f  $$(docker images -q -f "dangling=true")
rm:
	docker rm $$(docker ps -q -f 'status=exited')
clean:
	docker rmi -f keboola/tde-exporter
cleandatatdir:
	-sudo rm -rf $(DATADIR)/out
cleantestdatadir:
	-sudo rm -rf $(TESTDATADIR)/out
cleanall: rmi clean rm
