#import sys
#import os

class Unbuffered:

   def __init__(self, logfile, stdin, stdout):

       self.te = open(logfile, 'w')  # File where you need to keep the logs
       self.stdin = stdin
       self.stdout = stdout

   def write(self, data):

       self.stdout.write(data)
       self.stdout.flush()
       self.te.write(data)    # Write the data of stdout here to a text file as well
       self.te.flush()

   def readline(self):
       
       data = self.stdin.readline()
       self.te.write(data)
       self.te.flush()
       return data


   def flush(self):
 
       self.stdin.flush()
       self.stdout.flush()
       self.te.flush()
