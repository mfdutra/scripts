#!/usr/bin/python -u

# Creates a list of list of files, where each list is not bigger than a
# specified size. Useful to backup a big directory into fixed-size medias, like
# DVDs.

# Copyright 2012 Marlon Dutra
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import os.path
import sys
import tempfile

if len(sys.argv) < 3:
	print >> sys.stderr, 'Usage: %s directory max-size' % (sys.argv[0])
	sys.exit(1)

class File:
	def __init__(self, name):
		self.name = name
		self.size = 0

	def __repr__(self):
		return 'File: %s (%d bytes)' % (self.name, self.size)

def walkDir(root):
	for obj in sorted(os.listdir(root)):
		if os.path.isdir(root + '/' + obj):
			walkDir(root + '/' + obj)

		elif os.path.isfile(root + '/' + obj):
			fileObj = File(root + '/' + obj)
			fileObj.size = os.stat(root + '/' + obj)[6]
			fileList.append(fileObj)

directory = sys.argv[1]
size = int(sys.argv[2])
fileList = []
chunks = []

# walk recursively the directory and create the list the of files, depth first
# and sorted by name
walkDir(directory)

print '%d files found' % (len(fileList))

leftSpace = size
currentChunk = []
for f in fileList:
	if f.size > size:
		print >> sys.stderr, 'ERROR: A single file (%s) is bigger (%d bytes) than the chunk size (%d bytes)' % (f.name, f.size, size)
		sys.exit(2)

	if f.size <= leftSpace:
		leftSpace -= f.size
		currentChunk.append(f)

	else: # chunk size exceeded
		print 'Chunk: %d files - %d bytes' % (len(currentChunk), (size-leftSpace))
		chunks.append(currentChunk)
		currentChunk = []
		leftSpace = size
		leftSpace -= f.size
		currentChunk.append(f)

if currentChunk: # append last chunk
	print 'Chunk: %d files - %d bytes' % (len(currentChunk), (size-leftSpace))
	chunks.append(currentChunk)

exportDir = tempfile.mkdtemp()
print 'Exporting %d chunks to directory %s' % (len(chunks), exportDir)

i = 1
for chunk in chunks:
	fileName = 'chunk-%04d' % i
	i += 1
	fd = open(exportDir + '/' + fileName, 'w')
	for f in chunk:
		print >> fd, f.name
	fd.close()
	print fileName
