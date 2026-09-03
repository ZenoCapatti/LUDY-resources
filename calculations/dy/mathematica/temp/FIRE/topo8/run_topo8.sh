#!/bin/bash
	cd '/Users/zeno/Documents/analytic_calculations_DY/temp/FIRE/topo8'
	'/Users/zeno/Documents/fire/FIRE6/poly/FIRE6' -c topo8
	exit_code=$?
	echo __EXIT_CODE__:$exit_code
	exit $exit_code
	