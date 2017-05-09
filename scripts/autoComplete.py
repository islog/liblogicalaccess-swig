#!/usr/bin/env python

import sys
import os
import glob
import re
import clang.cindex

regexsharedptr = r"(?<=std::shared_ptr<)(.*?)(?=>)"
regexns = r"(?<=namespace )(.*?)(?=\n)"
includebase = "<logicalaccess{0}>"
include = []
nest = []
classlist = []

def	parsesharedptr(content):
	ns = re.findall(regexns, content)
	matches = re.finditer(regexsharedptr, content)
	for match in matches:
		strmatch = str(match[0])
		nbr = strmatch.count('<')
		while nbr > 0:
			strmatch += str('>')
			nbr -= 1
		if "::" not in strmatch:
			strmatch = "::".join(ns) + "::" + strmatch
		if "std::" not in strmatch and strmatch not in classlist:
			classlist.append(strmatch)

def	includeprocess(path, category):
	if len(glob.glob(path, recursive=True)) == 0:
		print ("[ERROR]: nothing found in " + path)
	for filename in glob.glob(path, recursive=True):
		with open(filename, "r") as f:
			content = f.read()
			filename = filename.replace("\\", "/").split("logicalaccess")[-1]
			include.append((category, includebase.replace("{0}", filename)))
			parsesharedptr(content)


def cleandoc(path):
	with open(path, "r") as f:
		lines = f.readlines()
		a = lines.index("/* Additional_include */\n") + 1
		while a != lines.index("/* END_Additional_include */\n") - 1:
			del lines[a]
		a = lines.index("/* Include_section */\n") + 1
		while a != lines.index("/* END_Include_section */\n") - 1:
			del lines[a]
	return lines

def	lookdata(curcat):
	retinclude = []
	for cat, inc in include:
		if curcat == cat:
			retinclude.append(inc)
	return retinclude
	
def includewrite():
	path = "../LibLogicalAccessNet.win32/liblogicalaccess{0}.i"
	
	cardpath = path.replace("{0}", "_core")
	cardinc = lookdata("CORE")
	lines = cleandoc(cardpath)
	i = 0
	while i < len(lines):
		if "/* Additional_include */\n" in lines[i]:
			i += 2
			for cinc in cardinc:			
				lines.insert(i, "#include {0}\n".format(cinc))
				i += 1
			lines.insert(i, "\n")
			i += 1
		if "/* Include_section */\n" in lines[i]:
			i += 2
			for cinc in cardinc:			
				lines.insert(i, "%include {0}\n".format(cinc))
				i += 1
			lines.insert(i, "\n")
			i += 1
		i += 1	
	with open(cardpath, "w") as f:
		f.write(''.join(lines))
	
	cardpath = path.replace("{0}", "_card")
	cardinc = lookdata("CARD")
	lines = cleandoc(cardpath)
	i = 0
	while i < len(lines):
		if "/* Additional_include */\n" in lines[i]:
			i += 2
			for cinc in cardinc:
				lines.insert(i, "#include {0}\n".format(cinc))
				i += 1
			lines.insert(i, "\n")
			i += 1
		if "/* Include_section */\n" in lines[i]:
			i += 2
			for cinc in cardinc:
				lines.insert(i, "%include {0}\n".format(cinc))
				i += 1
			lines.insert(i, "\n")
			i += 1
		i += 1	
	with open(cardpath, "w") as f:
		f.write(''.join(lines))
		
	readerpath = path.replace("{0}", "_reader")
	readerinc = lookdata("READER")
	lines = cleandoc(readerpath)
	i = 0
	while i < len(lines):
		if "/* Additional_include */\n" in lines[i]:
			i += 2
			for rinc in readerinc:
				lines.insert(i, "#include {0}\n".format(rinc))
				i += 1
			lines.insert(i, "\n")
			i += 1
		if "/* Include_section */\n" in lines[i]:
			i += 2
			for rinc in readerinc:
				lines.insert(i, "%include {0}\n".format(rinc))
				i += 1
			lines.insert(i, "\n")
			i += 1
		i += 1	
	with open(readerpath, "w") as f:
		f.write(''.join(lines))
		
	cryptopath = path.replace("{0}", "_crypto")
	cryptoinc = lookdata("CRYPTO")
	lines = cleandoc(cryptopath)
	i = 0
	while i < len(lines):
		if "/* Additional_include */\n" in lines[i]:
			i += 2
			for crinc in cryptoinc:
				lines.insert(i, "#include {0}\n".format(crinc))
				i += 1
			lines.insert(i, "\n")
			i += 1
		if "/* Include_section */\n" in lines[i]:
			i += 2
			for crinc in cryptoinc:
				lines.insert(i, "%include {0}\n".format(crinc))
				i += 1
			lines.insert(i, "\n")
			i += 1
		i += 1	
	with open(cryptopath, "w") as f:
		f.write(''.join(lines))
	
def find_classdecl(node, filename):
	global curnamespace
	for c in node.get_children():
		if c.kind == clang.cindex.CursorKind.CLASS_DECL and c.location.file.name == filename:
			if len(nest) == 0:
				if c.spelling not in classlist:
					classlist.append(c.spelling)
			else:
				if "::".join(nest) + "::" + c.spelling not in classlist:
					classlist.append("::".join(nest) + "::" + c.spelling)
			find_classdecl(c, filename)		
		elif c.kind == clang.cindex.CursorKind.NAMESPACE and c.location.file.name == filename:
			nest.append(c.spelling)
			find_classdecl(c, filename)
		if len(nest) > 0 and nest[-1] == c.spelling:
			nest.pop()
	
def	sharedptrprocess():
	clang.cindex.Config.set_library_file('C:/Program Files/LLVM/bin/libclang.dll')
	index = clang.cindex.Index.create()
	options = clang.cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | clang.cindex.TranslationUnit.PARSE_INCOMPLETE
	for filename in glob.glob("../packages/include/logicalaccess/**/*.hpp", recursive=True):
		tu = index.parse(filename, ['-x', 'c++', '-std=c++11', '-DLIBLOGICALACCESS_API='], unsaved_files=None, options=options)
		print ('Translation unit:', tu.spelling)
		find_classdecl(tu.cursor, filename)
	classlist.sort()
	
def	sharedptrwrite():
	path = "../LibLogicalAccessNet.win32/liblogicalaccess.i"
	with open(path, "r") as f:
		lines = f.readlines()
		i = lines.index("/*****SHARED PTR SECTION*****/\n") + 1
		while i != lines.index("/*****POST PROCESSING INSTRUCTIONS*****/\n") - 1:
			del lines[i]
	i = lines.index("/*****SHARED PTR SECTION*****/\n") + 1
	lines.insert(i, "\n")
	i += 1
	for sptr in classlist:
		lines.insert(i, "%shared_ptr(" + sptr + ");" + "\n")
		i += 1
	for sptr in classlist:
		lines.insert(i, "%shared_ptr(" + sptr.split("::")[-1] + ");" + "\n")
		i += 1
	with open(path, "w") as f:
		f.write(''.join(lines))
		
def main():
	includeprocess("../packages/include/logicalaccess/cards/**/*.hpp", "CORE")
	includeprocess("../packages/include/logicalaccess/plugins/cards/**/*.hpp", "CARD")
	includeprocess("../packages/include/logicalaccess/readerproviders/**/*.hpp", "CORE")
	includeprocess("../packages/include/logicalaccess/plugins/readers/**/*.hpp", "READER")
	includeprocess("../packages/include/logicalaccess/crypto/**/*.hpp", "CRYPTO")
	sharedptrprocess()
	sharedptrwrite()
	includewrite()
main()
