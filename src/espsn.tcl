source "application.tcl"

set input_file_name [lindex $argv 0]
set output_file_name [lindex $argv 1]
if {[llength $argv] == 3} {
    set espsn_experiment_data [lindex $argv 2]
    set is_generative 1
} else {
    set is_generative 0
}

set input_file [open $input_file_name]

set N [lindex [split [gets $input_file] ":"] 1]
set duration [lindex [split [gets $input_file] ":"] 1]
set link_bps [lindex [split [gets $input_file] ":"] 1]
set link_delay [lindex [split [gets $input_file] ":"] 1]
set queue_limit [lindex [split [gets $input_file] ":"] 1]
set k [lindex [split [gets $input_file] ":"] 1]

set esn_init_time [lindex [split [gets $input_file] ":"] 1]
set esn_training_time [lindex [split [gets $input_file] ":"] 1]
set esn_dt [lindex [split [gets $input_file] ":"] 1]
set input_ch_num [lindex [split [gets $input_file] ":"] 1]
gets $input_file

set line [gets $input_file]
while { $line != "" } {
    set src_dst_type [split $line " "]
    lappend topology $src_dst_type
    set line [gets $input_file]
}

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


set trace_file_name "$output_file_name.tr"
set nam_file_name "$output_file_name.nam"
set tcp_file_name "$output_file_name.tcp"
set network_file_name "$output_file_name.network"

puts "--------------------"
puts "Setting File: $input_file_name"
puts "Output File: $output_file_name.\{tr|tcp|tam\}"
puts "N: $N"
puts "Duration: $duration"
puts "Input Channel Num: $input_ch_num"
puts "Link: $link_bps, $link_delay, $queue_limit packets queue"
puts "k: $k"
puts "--------------------"


puts "\033\[32m\[PSN\]\033\[39m initializing simulator..."
set ns [new Simulator]
$ns at $duration "exit 0"

#set tracefile [open $trace_file_name w]
#$ns trace-all $tracefile
#set namfile [open $nam_file_name w]
#$ns namtrace-all $namfile
set tcpfile [open $tcp_file_name w]
#Agent/TCP set trace_all_oneline_ true


puts "\033\[32m\[PSN\]\033\[39m creating nodes..."
for {set i 0} {$i < $N} {incr i} {
    set node($i) [$ns node]
}


puts "\033\[32m\[PSN\]\033\[39m creating link topology..."
set link_params "$link_bps $link_delay DropTail"
for {set i 0} {$i < $N-1} {incr i} {
    # 1-d grid
    eval \$ns duplex-link \$node(\$i) \$node([expr \$i + 1]) $link_params
    $ns queue-limit $node($i) $node([expr $i + 1]) $queue_limit
    $ns queue-limit $node([expr $i + 1]) $node($i) $queue_limit

    # random graph
    # for {set j [expr $i + 1]} {$j < $N} {incr j} {
    #   if { 0.5 < [expr rand()]} {
    #     #puts [format "  node(%d) <-> node(%d)" $i $j]
    #     eval \$ns duplex-link \$node(\$i) \$node(\$j) $link_params
    #     $ns queue-limit $node($i) $node($j) $queue_limit
    #     $ns queue-limit $node($j) $node($i) $queue_limit
    #     puts $networkfile [format "%d %d" $i $j]
    #   }
    # }
}
eval \$ns duplex-link \$node(0) \$node([expr \$N - 1]) $link_params
$ns queue-limit $node(0) $node([expr $N - 1]) $queue_limit
$ns queue-limit $node([expr $N - 1]) $node(0) $queue_limit


puts "\033\[32m\[PSN\]\033\[39m creating flows..."
set flows []
foreach flow_setting $topology {
    set src [lindex $flow_setting 0]
    set dst [lindex $flow_setting 1]
    set input_ch [lindex $flow_setting 2]
    set pos_neg [lindex $flow_setting 3]

    set tcp [new Agent/TCP/Newreno]
    set sink [new Agent/TCPSink]
    $tcp trace cwnd_
    $tcp attach-trace $tcpfile
    $ns attach-agent $node($src) $tcp
    $ns attach-agent $node($dst) $sink
    $ns connect $tcp $sink
    $tcp set fid_ [llength $flows]

    if { $is_generative } {
        set flow [new Application/FTP]
    } else {
        if { $pos_neg == 1 } {
            set flow [new Application/InputFlow $input($input_ch)]
        } else {
            set flow [new Application/InputFlowReverse $input($input_ch)]
        }
    }
    lappend flows $flow
    $flow attach-agent $tcp
}

set python_generative_interface espsn_interface_generative.py
proc update-ns-input {} {
    global python_generative_interface
    global flows
    global ns
    global esn_dt
    set now [$ns now]
    set esnout [ exec python $python_generative_interface ]
    for {set i 0} {$i < [llength $flows]} {incr i 1} {
        set flow [lindex $flows $i]
        $ns at [expr $now] "$flow start"
        $ns at [expr $now + $esn_dt * $esnout] "$flow stop"
    }
}

if { $is_generative } {
    for {set i 0} {$i < [expr $duration / $esn_dt]} {incr i} {
        set t [expr $i * $esn_dt]
        $ns at $t "update-ns-input"
    }
    for {set i 0} {$i <= $duration} {incr i 1} {
        $ns at $i "puts { time: $i}"
    }
} else {
    for {set i 0} {$i <= $duration} {incr i 100} {
        $ns at $i "puts { time: $i}"
    }
}



puts "\033\[32m\[PSN\]\033\[39m simulation..."
$ns run
