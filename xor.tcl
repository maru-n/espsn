# quasi-1D simulation

source "periodic.tcl"

# parameters

set duration 40.0
set output_file_name "data/test_xor"
set trace_file_name "$output_file_name.tr"
set nam_file_name "$output_file_name.nam"
set tcp_file_name "$output_file_name.tcp"

puts $trace_file_name

set N 20

#
# node0 --- node1 --- node2 ... nodeN
#

#set flows 15
set link_param {10Mb 10ms DropTail}
set queue_limit 10

#set cycle 10.0
#set duty 1.0

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
  puts [format "  node(%d)" $i]
  set node($i) [$ns node]
}

puts "creating topology..."
for {set i 0} {$i < $N-1} {incr i} {
  puts [format "  node(%d) <-> node(%d)" $i [expr $i + 1]]
  eval \$ns duplex-link \$node(\$i) \$node([expr \$i + 1]) $link_param
  $ns queue-limit $node($i) $node([expr $i + 1]) $queue_limit
  $ns queue-limit $node([expr $i + 1]) $node($i) $queue_limit
}

puts "creating flows..."
for {set i 0} {$i < $N} {incr i} {
  for {set j 0} {$j < $N} {incr j} {
    if { $i == $j } {continue}
    set flow_id [expr $i * $N + $j]
    if { $i < $N / 2 } {
      set cycle 4.0
      set duty 0.5
    } else {
      set cycle 2.0
      set duty 0.5
    }
    puts [format "  flow: node(%d) -> node(%d) : cycle=%f duty=%f" $i $j $cycle $duty]
    set tcp [new Agent/TCP/Newreno]
    set sink [new Agent/TCPSink]
    $tcp attach-trace $tcpfile
    $tcp trace cwnd_
    $ns attach-agent $node($i) $tcp
    $ns attach-agent $node($j) $sink
    $ns connect $tcp $sink
    $tcp set fid_ $flow_id
    $ns color 0 blue
    set flow [new Application/PeriodicFTP $cycle $duty]
    $flow attach-agent $tcp
    $ns at 0.0 "$flow run"
  }
}

puts "starting simulation..."
$ns run
