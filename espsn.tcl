source "input_flow.tcl"

#
# node0 --- node1 --- node2 ... nodeN
#

# file format
# ------------------------
# N
# duration [sec]
# link-bps (10Mb)
# link-delay (10ms)
# queue-limit (10)
# input_ch_num
#
# time node[0]{0|1} node[1]{0|1} node[2]{0|1} ... target_signal{0|1}
# time node[0]{0|1} node[1]{0|1} node[2]{0|1} ... target_signal{0|1}
# time node[0]{0|1} node[1]{0|1} node[2]{0|1} ... target_signal{0|1}
#    .
#    .
#    .
#    .
# ------------------------

set input_file_name [lindex $argv 0]
set output_file_name [lindex $argv 1]

set input_file [open $input_file_name]

set N [lindex [split [gets $input_file] ":"] 1]
set duration [lindex [split [gets $input_file] ":"] 1]
set link_bps [lindex [split [gets $input_file] ":"] 1]
set link_delay [lindex [split [gets $input_file] ":"] 1]
set queue_limit [lindex [split [gets $input_file] ":"] 1]
# esn settings on 3 lines, not used on ns-2
gets $input_file
gets $input_file
gets $input_file
set input_ch_num [lindex [split [gets $input_file] ":"] 1]
gets $input_file

while { ! [eof $input_file] } {
  set line [gets $input_file]
  set val [split $line " "]
  set time [lindex $val 0]
  for {set input_ch 0} {$input_ch < $input_ch_num} {incr input_ch} {
    set state [lindex $val $input_ch+1]
    lappend input($input_ch) "$time $state"
  }
}
close $input_file

set link_params "$link_bps $link_delay DropTail"

set trace_file_name "$output_file_name.tr"
set nam_file_name "$output_file_name.nam"
set tcp_file_name "$output_file_name.tcp"

puts "--------------------"
puts "Setting File: $input_file_name"
puts "Output File: $output_file_name.\{tr|tcp|tcl\}"
puts "N: $N"
puts "Duration: $duration"
puts "Input Channel Num: $input_ch_num"
puts "Link: $link_bps, $link_delay, $queue_limit packets queue"
puts "--------------------"


puts "initializing simulator..."
set ns [new Simulator]
$ns at $duration "exit 0"

set tracefile [open $trace_file_name w]
$ns trace-all $tracefile
set namfile [open $nam_file_name w]
$ns namtrace-all $namfile
set tcpfile [open $tcp_file_name w]
Agent/TCP set trace_all_oneline_ true

puts "creating nodes..."
# $ns_node(0:N) node (TCP client or server)
for {set i 0} {$i < $N} {incr i} {
  # puts [format "  node(%d)" $i]
  set node($i) [$ns node]
}

puts "creating topology..."
for {set i 0} {$i < $N-1} {incr i} {
  # puts [format "  node(%d) <-> node(%d)" $i [expr $i + 1]]
  eval \$ns duplex-link \$node(\$i) \$node([expr \$i + 1]) $link_params
  $ns queue-limit $node($i) $node([expr $i + 1]) $queue_limit
  $ns queue-limit $node([expr $i + 1]) $node($i) $queue_limit
}

puts "creating flows..."
for {set i 0} {$i < $N} {incr i} {
  for {set j 0} {$j < $N} {incr j} {
    if { $i == $j } {continue}
    set flow_id [expr $i * $N + $j]
    set input_ch [expr $i / ($N / $input_ch_num)]
    # puts [format "  flow: node(%d) -> node(%d) input(%d)" $i $j $input_ch]
    set tcp [new Agent/TCP/Newreno]
    set sink [new Agent/TCPSink]
    $tcp attach-trace $tcpfile
    $tcp trace cwnd_
    $ns attach-agent $node($i) $tcp
    $ns attach-agent $node($j) $sink
    $ns connect $tcp $sink
    $tcp set fid_ $flow_id
    $ns color 0 blue
    set flow [new Application/InputFlow $input($input_ch)]
    $flow attach-agent $tcp
    #$ns at 0.0 "$flow run"
  }
}

puts "starting simulation..."
$ns run
