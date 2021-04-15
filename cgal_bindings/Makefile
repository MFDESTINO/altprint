all:
	$(MAKE) -C y_monotone_partition
	mkdir -p ../altprint/path/cgal_bindings/y_monotone_partition
	cp y_monotone_partition/_y_monotone_partition.so ../altprint/path/cgal_bindings/y_monotone_partition
	cp y_monotone_partition/y_monotone_partition.py ../altprint/path/cgal_bindings/y_monotone_partition
	cp cgal_bindings.py ../altprint/path/cgal_bindings/

clean:
	$(MAKE) -C y_monotone_partition clean
	rm -rf ../altprint/path/cgal_bindings/
