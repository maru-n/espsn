source "application.tcl"

set PY_GENERATIVE_INTERFACE_SCRIPT "|./esn_interface_generative.py 2>../generative.error"

set input_file_name [lindex $argv 0]
set output_file_name [lindex $argv 1]
if {[llength $argv] == 4} {
    set training_data [lindex $argv 2]
    set is_generative 1
    set duration_generative [lindex $argv 3]
} else {
    set is_generative 0
}

set input_file [open $input_file_name]

#set N [lindex [split [gets $input_file] ":"] 1]
#set duration_predictive [lindex [split [gets $input_file] ":"] 1]
#set link_bps [lindex [split [gets $input_file] ":"] 1]
#set link_delay [lindex [split [gets $input_file] ":"] 1]
#set link_queue [lindex [split [gets $input_file] ":"] 1]
#set k [lindex [split [gets $input_file] ":"] 1]
#set esn_init_time [lindex [split [gets $input_file] ":"] 1]
#set esn_training_time [lindex [split [gets $input_file] ":"] 1]
#set esn_dt [lindex [split [gets $input_file] ":"] 1]
#set input_num [lindex [split [gets $input_file] ":"] 1]
#gets $input_file

set param_list {
    N
    duration
    link_bps
    link_delay
    link_queue
    k
    esn_init_time
    esn_training_time
    esn_dt
    input_num
    continuous
}

set line [gets $input_file]
while { $line != "" } {
    set param [lindex [split $line ":"] 0]
    set val   [lindex [split $line ":"] 1]
    if { [lsearch $param_list $param] != -1} {
        set $param $val
    }
    set line [gets $input_file]
}
set duration_predictive $duration

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
    for {set input_ch 0} {$input_ch < $input_num} {incr input_ch} {
        set state [lindex $val $input_ch+1]
        lappend input($input_ch) "$time $state"
    }
}
close $input_file


set trace_file_name "$output_file_name.tr"
set nam_file_name "$output_file_name.nam"
set tcp_file_name "$output_file_name.tcp"
set network_file_name "$output_file_name.network"

if {$is_generative} {
    puts "\033\[31m\[GENERATIVE\]\033\[39m"
    puts "-- Setting File: $input_file_name"
    puts "-- Output File: $output_file_name.\{tr|tcp|tam\}"
    #puts "Continuous": $continuous
    puts "-- N: $N"
    puts "-- Duration: $duration_generative"
    puts "-- Input Channel Num: $input_num"
    puts "-- Link: $link_bps, $link_delay, $link_queue packets queue"
    puts "-- k: $k"
} else {
    puts "\033\[31m\[PREDICTIVE\]\033\[39m"
    puts "-- Setting File: $input_file_name"
    puts "-- Output File: $output_file_name.\{tr|tcp|tam\}"
    #puts "Continuous": $continuous
    puts "-- N: $N"
    puts "-- Duration: $duration_predictive (initialization-end:$esn_init_time training-end:$esn_training_time)"
    puts "-- Input Channel Num: $input_num"
    puts "-- Link: $link_bps, $link_delay, $link_queue packets queue"
    puts "-- k: $k"
}

puts "\033\[32m\[PSN\]\033\[39m initializing simulator..."
set ns [new Simulator]
if {$is_generative} {
    $ns at $duration_generative "exit 0"
} else {
    $ns at $duration_predictive "exit 0"
}
#set tracefile [open $trace_file_name w]
#$ns trace-all $tracefile
#set namfile [open $nam_file_name w]
#$ns namtrace-all $namfile

if {$is_generative} {
    set py_generative_interface [open $PY_GENERATIVE_INTERFACE_SCRIPT "r+"]
    puts $py_generative_interface $training_data
    puts $py_generative_interface $tcp_file_name
    set generative_file_name "$output_file_name.gen.txt"
    puts $py_generative_interface $generative_file_name
} else {
    set tcp_output [open $tcp_file_name w]
}
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
    $ns queue-limit $node($i) $node([expr $i + 1]) $link_queue
    $ns queue-limit $node([expr $i + 1]) $node($i) $link_queue
    # random graph
    # for {set j [expr $i + 1]} {$j < $N} {incr j} {
    #   if { 0.5 < [expr rand()]} {
    #     #puts [format "  node(%d) <-> node(%d)" $i $j]
    #     eval \$ns duplex-link \$node(\$i) \$node(\$j) $link_params
    #     $ns queue-limit $node($i) $node($j) $link_queue
    #     $ns queue-limit $node($j) $node($i) $link_queue
    #     puts $networkfile [format "%d %d" $i $j]
    #   }
    # }
}
eval \$ns duplex-link \$node(0) \$node([expr \$N - 1]) $link_params
$ns queue-limit $node(0) $node([expr $N - 1]) $link_queue
$ns queue-limit $node([expr $N - 1]) $node(0) $link_queue


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
    if { $is_generative } {
        $tcp attach-trace $py_generative_interface
    } else {
        $tcp attach-trace $tcp_output
    }
    $ns attach-agent $node($src) $tcp
    $ns attach-agent $node($dst) $sink
    $ns connect $tcp $sink
    $tcp set fid_ [llength $flows]

    if { $is_generative } {
        if { $pos_neg == 1 } {
            set flow [new Application/InputRealtimeFlow]
        } else {
            set flow [new Application/InputRealtimeFlowReverse]
        }
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

proc update-ns-input {} {
    global py_generative_interface
    global flows
    global ns
    global esn_dt
    set now [$ns now]

    #flush $py_generative_interface
    puts $py_generative_interface "update"
    flush $py_generative_interface
    set update_data [split [gets $py_generative_interface] " "]
    set pwm_duty [lindex $update_data 0]

    for {set i 0} {$i < [llength $flows]} {incr i 1} {
        set flow [lindex $flows $i]
        $ns at $now "$flow input_on"
        $ns at [expr $now + $esn_dt * $pwm_duty] "$flow input_off"
    }
    $ns at [expr $now + $esn_dt] "update-ns-input"
}

if { $is_generative } {
    $ns at 0 "update-ns-input"
#    for {set i 0} {$i < [expr $duration_generative / $esn_dt]} {incr i} {
#        set t [expr $i * $esn_dt]
#        $ns at $t "update-ns-input"
#    }
    for {set i 0} {$i <= $duration_generative} {incr i 10} {
        $ns at $i "puts -nonewline {\r $i/$duration_generative }; flush stdout"
    }
    $ns at [expr $duration_generative - 1] "puts \"\""
} else {
    for {set i 0} {$i <= $duration_predictive} {incr i 10} {
        $ns at $i "puts -nonewline {\r $i/$duration_predictive }; flush stdout"
    }
    $ns at [expr $duration_predictive - 1] "puts \"\""
}



puts "\033\[32m\[PSN\]\033\[39m simulation..."
$ns run
