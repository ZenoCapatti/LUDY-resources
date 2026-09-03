#!/bin/bash
	cd '/Users/lcnbr/dev/work/bern/LUDY/DIS_DY_analytic/temp/FIRE/topo4'
	'/Users/lcnbr/dev/work/bern/LUDY/DIS_DY_analytic/tools/fire/FIRE6/poly/FIRE6' -c topo4
	exit_code=$?
	echo __EXIT_CODE__:$exit_code
	exit $exit_code
	