all:
	make -C superscaffolder/ext/Gassst_v1.29
	make -C kmergenie
	#make -C minia # will be dynamically compiled

.FORCE:

test: .FORCE
	cd test ; ../gatb.sh ../reads/small_test_reads.fa
