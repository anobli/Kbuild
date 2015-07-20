#!/usr/bin/python

import os
import re
import sys
import glob
import getopt

def build_fixdep(path, out):
	os.system("gcc -o " + path + "/scripts/basic/fixdep " + path + "/scripts/basic/fixdep.c")

def install_fixdep(path, out):
	if not os.path.exists(out + "/scripts/basic"):
		os.makedirs(out + "/scripts/basic")
	os.system("cp " + path + "/scripts/basic/fixdep " + out + "/scripts/basic/fixdep")

def fixdep(path, out):
	build_fixdep(path, out)
	install_fixdep(path, out)

def srctree_scripts(res, file, line, line_number):
	new_line = line.replace("$(srctree)", "/usr/share/Kbuild")
	return new_line

def include_scripts(res, file, line, line_number):
	new_line = line.replace("scripts", "/usr/share/Kbuild/scripts")
	return new_line

def scripts(res, file, line, line_number):
	new_line = line.replace("scripts", "/usr/share/Kbuild/scripts")
	return new_line

def callback_no_rule(res, file, line, line_number):
	return line

def setup_regex(out):
	compiled_regexp = []
	if out == "/usr/share/Kbuild":
		REGEXP_GLOSSARY = [
			['^.*$', callback_no_rule]
		]
	else:
		REGEXP_GLOSSARY = [
			['^.*\$\(srctree\)/scripts/.*$', srctree_scripts],
			['^.*include scripts/.*$', include_scripts],
			['^.*scripts/.*$', scripts],
			['^.*$', callback_no_rule]
		]
		
	for regexp_string, regexp_rules in REGEXP_GLOSSARY:
		compiled_regexp.append([re.compile(regexp_string), regexp_rules])
	return compiled_regexp
		
def parse_line(compiled_regexp, file, line, line_number):
	for regexp, regexp_rules in compiled_regexp:
		res = regexp.search(line)
		if res:
			if regexp_rules:
				return regexp_rules(res, file, line, line_number)

def parse_file(path, out, file):
	compiled_regexp = setup_regex(out)
	fi = open(path + file, "r")
	if not os.path.exists(os.path.dirname(out + "/" + file)):
		os.makedirs(os.path.dirname(out + "/" + file))
	fo = open(out + "/" + file, "w")
	i = 0
	fi.seek(0)
	fo.seek(0)
	for line in fi:
		i += 1
		new_line = parse_line(compiled_regexp, file, line, i)
		fo.write(new_line)
	fi.close()
	fo.close()

def parse_files(path, out, files):
	for file in files:
		if "*" in file:
			glob_search = path + file
			for file in glob.glob(glob_search):
				if path != ".":
					f = file.replace(path, "")
				else:
					f = file.replace("./", "/")
				parse_file(path, out, f)
		else:
			parse_file(path, out, file)

def parse(linux_src, out):
	if not os.path.exists(out):
		os.makedirs(out)
	files = [
		"/scripts/Kbuild.include",
		"/scripts/Makefile*",
		"/scripts/basic/fixdep.c",
	]
	if out != "." and out != "./":
		files.append("/Makefile.app")
	parse_files(linux_src, out, files)

def print_help():
	print 'install.py [-i <kernel folder>] [-o <install folder>]'
	sys.exit()

def main(argv):
	kdir = "."
	idir = "/usr/share/Kbuild"

	try:
		opts, args = getopt.getopt(argv,"hi:o:")
	except getopt.GetoptError:
		print_help()
	for opt, arg in opts:
		if opt == '-h':
			print_help()
		elif opt  == "-i":
			kdir = arg
		elif opt == "-o":
			idir = arg
	if kdir == ".":
		fixdep(kdir, idir)
	parse(kdir, idir)

if __name__ == "__main__":
    main(sys.argv[1:])
