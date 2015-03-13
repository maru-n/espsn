import random

N = 10
duration = 80

dt = 0.01

target_file = open("target4.txt", 'w')
input_file = open("input4.txt", 'w')

input_file.write( "%d\n"%N )
input_file.write( "%d\n"%duration )
input_file.write( "2\n" )
input_file.write( "10Mb\n" )
input_file.write( "10ms\n" )
input_file.write( "10\n" )
input_file.write( "\n" )

for sec in range(duration):
    time = float(sec)
    if random.random() > 0.5:
        in1 = 1
    else:
        in1 = 0

    if random.random() > 0.5:
        in2 = 1
    else:
        in2 = 0
    input_file.write("%f 0 %d\n" % (time, in1))
    input_file.write("%f 1 %d\n" % (time, in2))
    for i in range(int(1/dt)):
        if (in1==1 and in2==1) or (in1==0 and in2==0):
            target_file.write("0 %d %d\n"%(in1, in2))
        else:
            target_file.write("1 %d %d\n"%(in1, in2))
