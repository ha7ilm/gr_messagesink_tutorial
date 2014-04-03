"""
Copyright (c) 2013 Andras Retzler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Version history
---------------
2013-08
- initial version

2013-11-12
- updated to GNU Radio 3.7
  - changed gr_message_sink_0_msgq_out to blocks_message_sink_0_msgq_out

2013-11-25
- almost rewritten, now supports multiple message sinks, and regexp_replaces

"""

import sys
import re

def main(filename, regexp_replaces=[]):
	f=open(filename,"r")
	data=f.read()
	f.close()
	
	#is it already converted?
	if data.count("(added by grcconvert)"):
		print "[grcconvert:info] File has already been converted: "+filename
		return 

	# process regexps
	for anything in regexp_replaces:
		data=re.sub(anything[0],anything[1],data)

	# count how many message sinks we have
	n_sinks=data.count("self.connect((self.blocks_message_sink_")
	print "[grcconvert:info] "+filename+" has {0} message sinks.".format(n_sinks)
	data=data.replace("self.connect((self.blocks_message_sink_","# removed by grcconvert: # self.connect((self.blocks_message_sink_")
	if not n_sinks:
		print "[grcconvert:error] No message sinks found."
		return

	lines=data.split("\n")

	# we find out where we should insert our line
	insert_here=0
	for i, l in enumerate(lines):
		if l.count("# Blocks"):
			insert_here=i
			break
	insert_here-=1
	if insert_here<=0:
		print "[grcconvert:error] Not a GNUradio-companion generated top_level.py file."
		return

	text="        ##################################################\n        # Message queues (added by grcconvert)\n        ##################################################\n"
	for i in range(0,n_sinks): text+="        self.msgq_out = blocks_message_sink_{0}_msgq_out = gr.msg_queue(2)\n".format(i)
	lines=lines[:insert_here]+[text]+lines[insert_here:]

	f=open(filename,"w")

	f.write("\n".join(lines))
	f.close()
	print "[grcconvert:info] converted:", filename
		
if __name__=="__main__":
	print "[grcconvert:info] msgq code inserter for GNUradio-companion generated top_level.py files"
	filename=sys.argv[1] if len(sys.argv)>1 else "top_block.py"
	main(filename)

