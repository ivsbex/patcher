# -*- coding: ansi -*-

from json import loads
from json.decoder import JSONDecodeError
from sys import exit
import argparse

def crit(msg):
	print("[!] " + str(msg))
	exit()

version = "1.0.1"

print("[i] Patcher v." + version)
print("[i] Author: Werryx")

parser = argparse.ArgumentParser(description = 'Patch files')
parser.add_argument('file', action = "store", help = 'Path to patching file')
parser.add_argument('patch', action = "store", help = 'Path to patch file')

args = parser.parse_args()

path = args.file
patch = args.patch
dpath = path

def doAfter(after):
	for i in after:
		if len(i) > 1:
			crit("'after' must be in this format:\n\"after\": [{\"first\": \"argument1\"}, {\"second\": 2}]")
		if "message" in i:
			print(i["message"])
		elif "exit" in i:
			exit(i["exit"])
		elif "patch" in i:
			doPatch(i["patch"]["path"].replace("$path", dpath), i["patch"]["patch"], True)
		elif "finish" in i:
			if i["finish"] is False:
				print("[i] File patched sucessfully")
			else:
				print("[i] File patched sucessfully")
				exit()

def doPatch(path, patch, recursion = False):
	if recursion is False:
		print("[*] Reading '" + path + "'...")
	try:
		try:
			fpatch = open(patch)
			patch = loads(fpatch.read())
			fpatch.close()
		except JSONDecodeError as e:
			crit("Patch file is incorrect")
	except FileNotFoundError:
		crit("Patch file does not exists")
	try:
		fpath = open(path, "rb")
		path = fpath.read()
		fpath.close()
	except FileNotFoundError:
		crit("Patching file does not exists")

	b = []
	for c in path:
		b.append(f"{c:02x}")

	if version not in patch["versions"]:
		if len(patch["versions"]) < 1:
			crit("Patch don't require any version of patcher")
		print("[!] Version of patcher don't match. Required one of")
		for i in patch["versions"]:
			print("- " + str(i))
		exit()

	if recursion is False:
		print("[*] Patching using '" + patch["name"] + "'...")
	for i in patch["patch"]:
		address = int(i["address"], 16)
		try:
			length = len(i["values"])
			values = i["values"]
		except KeyError:
			length = 1
			values = [i["value"]]
		addresses = []
		indexes = []
		for j in range(length):
			try:
				addresses.append(b[address + j])
				indexes.append(address + j)
			except IndexError:
				crit("Address out of range")
		if i["write"] is True:
			for num, adr in enumerate(indexes):
				if values[num] == b[adr]:
					continue
				b[adr] = values[num]
			try:
				doAfter(i["after"])
			except KeyError:
				pass
		elif i["write"] is False:
			for num, adr in enumerate(addresses):
				if values[num] == adr:
					continue
				try:
					doAfter(i["after"])
				except KeyError:
					pass
				break
		elif i["write"] == 2:
			for num, adr in enumerate(addresses):
				if values[num] == adr:
					try:
						doAfter(i["after"])
					except KeyError:
						pass
					break
	wfile = open(dpath, "wb")
	for bb in b:
		wfile.write(bytes.fromhex(bb))
	wfile.close()

doPatch(path, patch)

print("[i] File patched sucessfully")
