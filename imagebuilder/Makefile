.PHONY: build_packages build_repo build run clean

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

build_packages: package_repo
	# bluez-utils-compat
	cd packages && git clone https://aur.archlinux.org/bluez-utils-compat.git
	cd packages/bluez-utils-compat && BUILDDIR=/tmp/makepkg PKGDEST=../../package_repo makepkg -s

package_repo:
	mkdir package_repo

build_repo:
	cd package_repo && repo-add additional.db.tar.gz *.pkg.tar.zst

clean_repo:
	rm -rf packages/*
	rm -rf package_repo

pacman.conf: pacman.conf.in
	sed "s|##__PWD__##|$(ROOT_DIR)|g" pacman.conf.in > pacman.conf

build: build_repo pacman.conf
	sudo mkarchiso -v -w /tmp/archiso ./
	sudo rm -rf /tmp/archiso
run:
	run_archiso -i ./out/*

clean_output:
	rm -rf out

clean_build:
	sudo rm -rf /tmp/archiso
	rm -rf /tmp/makepkg

clean:
	rm pacman.conf

clean_all: clean clean_build clean_output clean_repo
